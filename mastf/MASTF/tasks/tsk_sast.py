# This file is part of MAST-F's Backend API
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
