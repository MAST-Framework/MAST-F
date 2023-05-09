# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor, Janbehere1
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
import zipfile

from datetime import datetime

from celery import shared_task, group, states
from celery.result import AsyncResult, GroupResult
from celery.utils.log import get_task_logger

from mastf.android.tools import apktool, baksmali
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
    Details(scan=scan, file=uploaded_file).save()
    scan.file = uploaded_file
    for name in names:
        Scanner(name=name, scan=scan).save()

    if not scan.start_date:
        scan.start_date = datetime.now()

    scan.save()
    if scan.start_date.date() == datetime.today().date():
        scan.status = "Active"
        scan.save()
        # The scan will be started whenever the right day is reached
        task_uuid = uuid.uuid4()
        global_task = ScanTask(task_uuid=task_uuid, scan=scan)
        # The task must be saved before the preparation is executed
        global_task.save()
        logger.info("Started global scan task on %s", scan.pk)

        result: AsyncResult = prepare_scan.delay(str(scan.pk), names)
        global_task.celery_id = result.id
        global_task.save()


@shared_task(bind=True)
def prepare_scan(self, scan_uuid: str, selected_scanners: list) -> AsyncResult:
    logger.info("Scan Peparation: Setting up directories of scan %s", scan_uuid)
    scan = Scan.objects.get(scan_uuid=scan_uuid)
    self.update_state(
        state="PROGRESS", meta={"current": 10, "detail": "Directory setup..."}
    )

    # Setup of special directories in our project directory:
    file_dir = scan.project.dir(scan.file.md5)

    # The first directory will store decompiled source code files,
    # and the second will store data that has been extracted initially.
    src = file_dir / "src"
    contents = file_dir / "contents"

    src.mkdir(exist_ok=True)
    contents.mkdir(exist_ok=True)
    self.update_state(
        state="PROGRESS", meta={"current": 30, "detail": "Extracting files"}
    )
    # TODO: add MIME type handlers (apk, ipa, aar, jar, dex); if no extension is given,
    # a default handler based on the scan type should be used.
    if scan.scan_type.lower() == "android":
        logger.info("Scan Peparation: Extracting files for scan %s", scan.pk)
        apktool.extractrsc(
            str(file_dir / scan.file.internal_name), str(contents), settings.APKTOOL
        )
        self.update_state(
            state="PROGRESS",
            meta={"current": 60, "detail": "Decompilation of binary files"},
        )

        smali_dir = src / "smali"
        smali_dir.mkdir(exist_ok=True)
        tool = settings.D2J_TOOLSET + "dex2smali"
        for path in contents.iterdir():
            # If we try to analyze an APK file, the files have to be decompiled
            # (currenlty only Smali)
            if path.suffix == "dex":
                baksmali.decompile(str(path), str(smali_dir), tool)

    else:
        with zipfile.ZipFile(str(file_dir / scan.file.internal_name)) as zfile:
            # Extract initial files
            zfile.extractall(str(contents))

    self.update_state(
        state="PROGRESS", meta={"current": 80, "detail": "Setting up scanners' tasks"}
    )
    for name in selected_scanners:
        scanner = Scanner.objects.get(project=scan.project, name=name)
        # Note that we're creating scan tasks before calling the asynchronous
        # group. The 'execure_scan' task will set the celery_id when it gets
        # executed.
        ScanTask(task_uuid=uuid.uuid4(), scan=scan, scanner=scanner).save()

    tasks = group(
        [execute_scan.s(str(scan.scan_uuid), name) for name in selected_scanners]
    )
    result: GroupResult = tasks.get()

    self.update_state(
        state=states.SUCCESS,
        meta={"current": 100, "detail": "Scanners have been started", "complete": True},
    )
    logger.info("Started scan with Group: %s", result)

    # Rather delete the finished task than setting its state to finished
    task = ScanTask.objects.filter(celery_id=self.id).first()
    task.active = False
    task.celery_id = None
    task.save()


@shared_task(bind=True)
def execute_scan(self, scan_uuid: str, plugin_name: str) -> AsyncResult:
    try:
        plugin = ScannerPlugin.all()[plugin_name]
        scan = Scan.objects.get(scan_uuid=scan_uuid)

        scanner = Scanner.objects.get(project=scan.project, name=plugin.internal_name)
        task = ScanTask.objects.get(scan=scan, scanner=scanner)

        # Before calling the actual task, the celery ID must be set in order
        # to fetch the current status.
        task.celery_id = self.id
        task.save()

        plugin.task(scan, task)
    except Exception:
        logger.exception("Unhandled worker exeption:")
