import logging
import uuid
import zipfile

from datetime import datetime

from celery import shared_task, group, states
from celery.result import AsyncResult, GroupResult

from mastf.android.tools import apktool
from mastf.MASTF import settings
from mastf.MASTF.models import (
    Scan,
    ScanTask,
    ProjectScanner,
    File,
    Details
)
from mastf.MASTF.scanners.plugin import ScannerPlugin

logger = logging.getLogger(__name__)

def schedule_scan(scan: Scan, uploaded_file: File, names: list) -> None:
    """Schedules the given scan.

    :param scan: the scan to be started
    :type scan: Scan
    :param file: the target file
    :type file: File
    """

    # First, create the scan details and save the scan file
    Details(scan=scan, file=uploaded_file).save()
    scan.file = uploaded_file

    if not scan.start_date:
        scan.start_date = datetime.now()

    scan.save()
    if scan.start_date.date() == datetime.today().date():
        scan.status = 'Active'
        scan.save()
        # The scan will be started whenever the right day
        # is reached
        task_uuid = uuid.uuid4()
        global_task = ScanTask(task_uuid=task_uuid, scan=scan)
        # The task must be saved before the preparation is executed
        global_task.save()

        result: AsyncResult = prepare_scan.delay(str(scan.scan_uuid), names)
        global_task.celery_id = result.id
        global_task.save()

@shared_task(bind=True)
def prepare_scan(self, scan_uuid: str, selected_scanners: list) -> AsyncResult:
    scan = Scan.objects.get(scan_uuid=scan_uuid)
    self.update_state(state='PROGRESS', meta={'current': 10, 'detail': "Directory setup..."})

    # Setup of special directories in our project directory:
    project_dir = settings.BASE_DIR / str(scan.project.project_uuid)
    file_dir = project_dir / str(scan.file.md5)
    file_dir.mkdir(exist_ok=True)

    # The first directory will store decompiled source code files,
    # and the second will store data that has been extracted initially.
    src = file_dir / 'src'
    contents = file_dir / 'contents'

    src.mkdir(exist_ok=True)
    contents.mkdir(exist_ok=True)

    self.update_state(state='PROGRESS', meta={'current': 30, 'detail': "Extracting files"})
    with zipfile.ZipFile(str(file_dir / scan.file.internal_name)) as zfile:
        # Extract initial files
        zfile.extractall(str(contents))

    self.update_state(state='PROGRESS', meta={'current': 60, 'detail': "Decompilation of binary files"})
    # If we try to analyze an APK file, the files have to be decompiled
    # (currenlty only Smali)
    if scan.scan_type.lower() == 'android':
        for path in contents.iterdir():
            if path.suffix == 'dex':
                apktool.decompile(str(path), str(src))

    self.update_state(state='PROGRESS', meta={'current': 80, 'detail': "Setting up scanners' tasks"})
    for name in selected_scanners:
        scanner = ProjectScanner.objects.get(project=scan.project, name=name)
        # Note that we're creating scan tasks before calling the asynchronous
        # group. The 'execure_scan' task will set the celery_id when it gets
        # executed.
        ScanTask(task_uuid=uuid.uuid4(), scan=scan, scanner=scanner).save()

    tasks = group([execute_scan.s(str(scan.scan_uuid), name) for name in selected_scanners])
    result: GroupResult = tasks.get()

    self.update_state(state=states.SUCCESS, meta={
        'current': 100, 'detail': "Scanners have been started",
        'complete': True
    })
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

        scanner = ProjectScanner.objects.get(project=scan.project, name=plugin.internal_name)
        task = ScanTask.objects.get(scan=scan, scanner=scanner)

        # Before calling the actual task, the celery ID must be set in order
        # to fetch the current status.
        task.celery_id = self.id
        task.save()

        plugin.task(scan, task)
    except Exception:
        logger.exception("Unhandled worker exeption:")


