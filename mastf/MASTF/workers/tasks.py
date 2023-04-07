import logging
import uuid

from celery import shared_task, group
from celery.result import AsyncResult, GroupResult

from mastf.MASTF.models import Scan, ScanTask, ProjectScanner
from mastf.MASTF.scanners.plugin import ScannerPlugin

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def prepare_scan(self, scan: Scan, selected_scanners: list) -> AsyncResult:
    plugins = ScannerPlugin.all()

    for name in selected_scanners:
        scanner = ProjectScanner.objects.get(project=scan.project, name=name)
        # Note that we're creating scan tasks before calling the asynchronous
        # group. The 'execure_scan' task will set the celery_id when it gets
        # executed.
        ScanTask(task_uuid=uuid.uuid4(), scan=scan, scanner=scanner).save()

    tasks = group([execute_scan.delay(scan, plugins[name]) for name in selected_scanners])
    result: GroupResult = tasks.get()



@shared_task(bind=True)
def execute_scan(self, scan: Scan, plugin: ScannerPlugin) -> AsyncResult:
    try:
        scanner = ProjectScanner.objects.get(project=scan.project, name=plugin.internal_name)
        task = ScanTask.objects.get(scan=scan, scanner=scanner)

        # Before calling the actual task, the celery ID must be set in order
        # to fetch the current status.
        task.celery_id = self.id
        task.save()

        plugin.task(scan, task)
    except Exception:
        logger.exception("Unhandled worker exeption:")


