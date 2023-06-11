from __future__ import annotations

import pathlib

from celery import shared_task
from celery.utils.log import get_task_logger

from mastf.core.progress import Observer

from mastf.MASTF import settings
from mastf.MASTF.models import ScanTask

logger = get_task_logger(__name__)

__all__ = ["perform_async_sast"]


@shared_task(bind=True)
def perform_async_sast(self, scan_task_id: str, file_dir) -> None:
    # We don't want to run into circular import chains
    from mastf.MASTF.scanners import code

    scan_task = ScanTask.objects.get(task_uuid=scan_task_id)
    scan_task.celery_id = self.request.id
    scan_task.save()
    observer = Observer(self, scan_task=scan_task)

    try:
        observer.update("Running pySAST scan...", do_log=True)
        code.sast_code_analysis(
            scan_task=scan_task,
            target_dir=pathlib.Path(file_dir) / "src",
            observer=observer,
            excluded=["re:.*/(android[x]?|kotlin[x]?)/.*"],
            rules_dirs=[settings.BASE_DIR / "android" / "rules"],
        )
        _, meta = observer.success("Finished pySAST scan!")
        return meta
    except Exception as err:
        _, meta = observer.exception(err, "Failed to execute pySAST successfully!")
        return meta
