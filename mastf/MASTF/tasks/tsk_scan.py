# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import uuid
import pathlib

from datetime import datetime
from typing import Callable

from celery import shared_task, group
from celery.result import AsyncResult, GroupResult
from celery.utils.log import get_task_logger

from mastf.core.files import TaskFileHandler
from mastf.core.progress import Observer

from mastf.MASTF import settings
from mastf.MASTF.models import Scan, ScanTask, Scanner, File, Details
from mastf.MASTF.scanners.plugin import ScannerPlugin

logger = get_task_logger(__name__)

__all__ = [
    "schedule_scan",
    "prepare_scan",
    "execute_scan",
]


def schedule_scan(scan: Scan, uploaded_file: File, names: list) -> None:
    """Schedules the given scan."""
    # First, create the scan details and save the scan file
    Details.objects.create(scan=scan)
    scan.file = uploaded_file
    for name in names:
        Scanner(name=name, scan=scan).save()

    if not scan.start_date:
        scan.start_date = datetime.now()

    scan.save()
    if scan.start_date.date() == datetime.today().date():
        scan.status = "Active"
        scan.is_active = True
        scan.save()
        # The scan will be started whenever the right day is reached
        task_uuid = uuid.uuid4()
        global_task = ScanTask(task_uuid=task_uuid, scan=scan, name="Scan Preparation Task")
        # The task must be saved before the preparation is executed
        global_task.save()
        logger.info("Started global scan task on %s", scan.pk)

        result: AsyncResult = prepare_scan.delay(str(scan.pk), names)
        global_task.celery_id = result.id
        global_task.save()


@shared_task(bind=True)
def prepare_scan(self, scan_uuid: str, selected_scanners: list) -> AsyncResult:
    logger.info("Scan Peparation: Setting up directories of scan %s", scan_uuid)

    task = ScanTask.objects.filter(celery_id=self.request.id).first()
    observer = Observer(self, scan_task=task)
    scan = Scan.objects.get(scan_uuid=scan_uuid)

    observer.update("Directory setup...", current=10)
    # Setup of special directories in our project directory:
    file_dir = scan.project.dir(scan.file.internal_name)
    file_path = scan.file.file_path

    # The first directory will store decompiled source code files,
    # and the second will store data that has been extracted initially.
    src = file_dir / "src"
    contents = file_dir / "contents"

    src.mkdir(exist_ok=True)
    contents.mkdir(exist_ok=True)
    observer.update("Extracting files...", current=30)
    # TODO: add MIME type handlers (apk, ipa, aar, jar, dex); if no extension is given,
    # a default handler based on the scan type should be used.
    handler = TaskFileHandler.from_scan(file_path, scan.scan_type)
    if not handler:
        # cancel scan
        _, meta = observer.fail("Could not find matching MIME-Type handler")
        logger.warning("Could not load file handler for MIME-Type: %s", file_path)
        return meta.get("description")

    handler.apply(pathlib.Path(file_path), file_dir, settings, observer=observer)
    observer.update("Creating scanner specific ScanTask objects.", current=80)

    plugins = ScannerPlugin.all()
    for name in selected_scanners:
        scanner = Scanner.objects.get(scan=scan, name=name)
        # Note that we're creating scan tasks before calling the asynchronous
        # group. The 'execute_scan' task will set the celery_id when it gets
        # executed.
        plugin = plugins[name]
        ScanTask.objects.create(
            task_uuid=uuid.uuid4(), scan=scan, scanner=scanner, name=plugin.name
        )

    tasks = group(
        [execute_scan.s(str(scan.scan_uuid), name) for name in selected_scanners]
    )
    # We actually don't need the group result object, we just have to execute
    # .get()
    result: GroupResult = tasks()
    _, meta = observer.success("Scanners have been started")
    logger.info("Started scan in Group: %s", result.id)

    # Rather delete the finished task than setting its state to finished
    return meta.get("description")


@shared_task(bind=True)
def execute_scan(self, scan_uuid: str, plugin_name: str) -> AsyncResult:
    try:
        logger.info("Running scan_task of <Scan %s, name='%s'>", scan_uuid, plugin_name)

        plugin = ScannerPlugin.all()[plugin_name]
        scan = Scan.objects.get(scan_uuid=scan_uuid)

        scanner = Scanner.objects.get(scan=scan, name=plugin.internal_name)
        task = ScanTask.objects.get(scan=scan, scanner=scanner)
        observer = Observer(self, scan_task=task)

        # Before calling the actual task, the celery ID must be set in order
        # to fetch the current status.
        task.celery_id = self.request.id
        task.save()

        plugin_task = plugin.task
        instance = plugin_task
        if isinstance(plugin_task, type):
            instance = plugin_task()

        if isinstance(instance, Callable):
            rvalue = instance(task, observer)
            _, meta = observer.success(
                "[%s] Finished scanner task", plugin_name
            )
            ScanTask.finish_scan(scan, task)
            rvalue = rvalue or meta
            return rvalue
        else:
            raise TypeError(
                "Unexpected task type %s; expected Callable[None, [Scan, ScanTask, Observer]]",
                type(instance),
            )
    except Exception as err:
        msg = "(%s) Unhandled worker exeption: %s" % (err.__class__.__name__, str(err))
        logger.exception(msg)
        _, meta = observer.exception(err, msg)
        ScanTask.finish_scan(scan, task)
        return meta.get("description")
