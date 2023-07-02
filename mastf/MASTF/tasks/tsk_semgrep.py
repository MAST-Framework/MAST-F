from __future__ import annotations

import os
import pathlib
import subprocess
import json

from celery import shared_task
from celery.utils.log import get_task_logger

from mastf.core.progress import Observer

from mastf.MASTF import settings
from mastf.MASTF.models import ScanTask, FindingTemplate, Finding, Snippet

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
        # Rather change the current working directory as .semgrepignore may be defined there
        # REVISIT: maybe use cwd=... in run()
        rules_dir,
        "&&",
        "semgrep",
        "scan",
        "-c",
        rules_dir,
        "--json",
        "--output",
        str(out_file),
        file_dir
    ]
    try:
        observer.update("Running semgrep...", do_log=True)
        result = subprocess.run(" ".join(cmd), capture_output=True, shell=True)
        result.check_returncode()

        observer.update("Finished semgrep, inspecing results...", do_log=True)
        with open(str(out_file), "r") as fp:
            data = json.load(fp)

        for result in data["results"]:
            # internal title := extra.metadata.area "-" extra.metadata.category "-(" check_id ")"
            internal_name = "%s-%s-(%s)" % (
                result["extra"]["metadata"]["area"].lower(),
                result["extra"]["metadata"]["category"].lower(),
                result["check_id"].split(".", 2)[-1].lower() # always something like "rules.storage.MSTG-STORAGE-7.2"
            )

            queryset = FindingTemplate.objects.filter(internal_id__startswith=internal_name)
            if queryset.exists() and len(queryset) == 1:
                template = queryset.first()
                path = pathlib.Path(result["path"])
                start = result["start"]["line"]
                end = result["end"]["line"]

                snippet = Snippet.objects.create(
                    sys_path=str(path),
                    language=path.suffix.removeprefix("."),
                    file_name=path.name,
                    file_size=path.stat().st_size,
                    lines=",".join([str(x) for x in range(start, end + 1)])
                )
                if not template.is_contextual:
                    Finding.create(template, snippet, scan_task.scanner)
                else:
                    Finding.create(template, snippet, scan_task.scanner, text=result["message"])

            _, meta = observer.success("Finished semgrep scan!")
            return meta
    except subprocess.CalledProcessError as err:
        _, meta = observer.exception(err, "Failed to execute semgrep!")
        return meta
    except Exception as oserr:
        _, meta = observer.exception(oserr, "Failed to read from semgrep results!")
        return meta.get("description")