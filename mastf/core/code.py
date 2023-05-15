# This file is part of MAST-F's Core API
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
import os
import re
import pathlib
import logging
import multiprocessing as mp

from yara_scanner import scan_file

from mastf.core.progress import Observer

from mastf.MASTF.utils.enum import Severity
from mastf.MASTF.settings import YARA_BASE_DIR
from mastf.MASTF.models import ScanTask, Finding, FindingTemplate, Snippet

logger = logging.getLogger(__name__)


class YaraResult:
    def __init__(self, match: dict) -> None:
        self._meta = match["meta"]
        self._severity = None
        self._template = None
        self.target = match["target"]

    @property
    def severity(self) -> Severity:
        if not self._severity:
            for sv in Severity:
                if str(sv).lower() == self.get("severity", Severity.NONE.value).lower():
                    self._severity = sv

        return self._severity

    @property
    def template_id(self) -> str:
        return self._meta.get("ft_id", None)

    @property
    def internal_id(self) -> str:
        return self._meta.get("ft_internal_id", None)

    def get_template_data(self) -> dict:
        return {
            key: self._meta.get(f"ft_fallback_{key}", "") for key in (
                "title", "description", "risk", "mitigation", "article"
            )
        }

    def get_template(self) -> FindingTemplate:
        if not self._template:
            # 1: Contains finding template ID or internal name?
            queryset = None
            if self.template_id:
                queryset = FindingTemplate.objects.filter(pk=self.template_id)
            elif self.internal_id:
                queryset = FindingTemplate.objects.filter(internal_name=self.internal_id)

            if queryset and queryset.exists():
                self._template = queryset.first()
            else:
                # 2: No finding template exists and we have to create one. This code
                # makes sure that no other template is mapped to the template's title.
                data = self.template_data
                if not data["title"]:
                    logger.warning("Invalid FindingTemplate definition: missing a valid title")
                    return None

                data["internal_name"] = re.sub(r"[\s_:]", "-", data["title"]).replace("--", "-")
                data["pk"] = FindingTemplate.make_uuid()
                data["default_severity"] = self.severity

                self._template = FindingTemplate.objects.create(**data)

        return self._template

    def __getitem__(self, key: str):
        return self._meta.get(key, None)

def yara_scan_file(file: pathlib.Path, task: ScanTask, base_dir=YARA_BASE_DIR, observer: Observer = None):
    for match in scan_file(str(file), str(base_dir)):
        result = YaraResult(match)

        template = result.get_template()
        if not template:
            if observer:
                observer.update("Skipping file: %s", str(file), do_log=True)
            else:
                logger.debug("Skipping file: %s", str(file))
            continue

        snippet = Snippet.objects.create(
            language=result["language"],
            file_name=result.target,
            file_size=os.path.getsize(str(file)),
            sys_path=str(file),
        )

        finding_id = Finding.make_uuid()
        Finding.objects.create(
            pk=finding_id,
            scan=task.scanner.scan,
            snippet=snippet,
            severity=result.severity,
            scanner=task.scanner,
            template=template,
        )


def yara_code_analysis(scan_task_pk: str, start_dir: str, observer: Observer = None,
                       base_dir: str = YARA_BASE_DIR):
    task = ScanTask.objects.get(pk=scan_task_pk)
    path = pathlib.Path(start_dir)
    if not path.exists():
        logger.warning("Could not validate start directory: %s", str(path))
    else:
        if observer:
            # Extra: use this function in your shared task and track the current progress
            # of this scan.
            observer.pos = 0
            observer.update("Starting YARA Scan...")

        for directory in path.glob("*/**"):
            # Reset the progres bar if
            if observer:
                if observer.pos >= 99:
                    observer.pos = 0
                observer.update("Scanning folder: '%s' ...", str(directory), do_log=True)

            if not mp.current_process().daemon:
                with mp.Pool(os.cpu_count()) as pool:
                    pool.starmap(yara_scan_file, [
                        (child, task, base_dir) for child in directory.iterdir() if not child.is_dir()
                    ])
            else:
                # As we can't use sub processes in a daemon process, we have to
                # call the function in a simple loop
                for child in directory.iterdir():
                    if child.is_dir():
                        continue

                    if observer and observer.pos >= 99:
                        observer.pos = 0
                        observer.update("Scanning file: '%s' ...", str(child), do_log=True)

                    yara_scan_file(child, task, base_dir)

