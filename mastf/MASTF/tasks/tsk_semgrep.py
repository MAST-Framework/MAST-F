from __future__ import annotations

import os
import pathlib
import subprocess
import json

from celery import shared_task
from celery.utils.log import get_task_logger

from mastf.core.progress import Observer

from mastf.MASTF import settings
from mastf.MASTF.models import ScanTask, FindingTemplate

logger = get_task_logger(__name__)

__all__ = ["perform_semgrep_scan"]

@shared_task(bind=True)
def perform_semgrep_scan(self, scan_task_id: str, rules_dir: str, file_dir: str) -> dict:
    scan_task = ScanTask.objects.get(task_uuid=scan_task_id)
    scan_task.celery_id = self.request.id
    scan_task.save()
    observer = Observer(self, scan_task=scan_task)

    out_file = pathlib.Path(file_dir) / "semgrep.json"
    if out_file.exists():
        os.remove(str(out_file))

    cmd = [ # cd rules_dir && semgrep -c rules_dir --output out_file --json file_dir
        "cd",
        rules_dir, # Rather change the current working directory as .semgrepignore may be defined there
        "&&",
        "semgrep",
        "scan",
        "-c",
        rules_dir,
        "--output",
        str(out_file),
        "--json",
        file_dir
    ]
    try:
        observer.update("Running semgrep...", do_log=True)
        result = subprocess.run(cmd, capture_output=True)
        result.check_returncode()

        observer.update("Finished semgrep, inspecing results...", do_log=True)
        with open(str(out_file), "r") as fp:
            data = json.load(fp)

        for result in data["results"]:
            # internal title := extra.metadata.area "-" extra.metadata.category "-(" check_id ")"
            internal_name = "%s-%s-(%s)" % (
                result["extra"]["metadata"]["area"].lower(),
                result["extra"]["metadata"]["category"].lower(),
                result["check_id"].lower()
            )

            queryset = FindingTemplate.objects.filter(internal_id=internal_name)
            if queryset.exists() and len(queryset) == 1:
                template = queryset.first()
                ... # TODO: define finding templates

    except subprocess.CalledProcessError as err:
        _, meta = observer.exception(err, "Failed to execute semgrep!")
        return meta
    except OSError as oserr:
        _, meta = observer.exception(oserr, "Failed to read from semgrep results!")
        return meta