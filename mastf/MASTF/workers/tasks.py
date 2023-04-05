import logging

from celery import shared_task
from celery.result import AsyncResult

from mastf.MASTF.models import Scan

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def prepare_scan(self, scan: Scan, selected_scanners: list) -> AsyncResult:
    pass
