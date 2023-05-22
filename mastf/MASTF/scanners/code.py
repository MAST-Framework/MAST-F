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

from concurrent.futures import ThreadPoolExecutor
from yara_scanner import scan_file

from mastf.core.progress import Observer

from mastf.MASTF.utils.enum import Severity
from mastf.MASTF.settings import YARA_BASE_DIR
from mastf.MASTF.models import ScanTask, Finding, FindingTemplate, Snippet, File

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
                if (
                    str(sv).lower()
                    == self._meta.get("severity", Severity.NONE.value).lower()
                ):
                    self._severity = sv

        return self._severity or Severity.INFO

    @property
    def template_id(self) -> str:
        return self._meta.get("ft_id", None)

    @property
    def internal_id(self) -> str:
        name = self._meta.get("ft_internal_id", None)
        if not name:
            return name

        return FindingTemplate.make_internal_id(name)

    def get_template_data(self) -> dict:
        return {
            key: self._meta.get(f"ft_fallback_{key}", "")
            for key in ("title", "description", "risk", "mitigation", "article")
        }

    def get_template(self) -> FindingTemplate:
        if not self._template:
            # 1: Contains finding template ID or internal name?
            queryset = None
            if self.template_id:
                queryset = FindingTemplate.objects.filter(pk=self.template_id)

            if self.internal_id:
                queryset = (queryset or FindingTemplate.objects).filter(
                    internal_id=self.internal_id
                )

            if queryset and queryset.exists():
                self._template = queryset.first()
            else:
                # 2: No finding template exists and we have to create one. This code
                # makes sure that no other template is mapped to the template's title.
                data = self.get_template_data()
                if not data["title"]:
                    logger.warning(
                        "Invalid FindingTemplate definition: missing a valid title"
                    )
                    return None

                data["internal_id"] = FindingTemplate.make_internal_id(data["title"])
                data["template_id"] = FindingTemplate.make_uuid()
                data["default_severity"] = self.severity

                self._template = FindingTemplate.objects.create(**data)

        return self._template

    def __getitem__(self, key: str):
        return self._meta.get(key, None)


def yara_scan_file(
    file: pathlib.Path,
    task: ScanTask,
    base_dir=YARA_BASE_DIR,
    observer: Observer = None,
):
    rel_path = File.relative_path(str(file))
    for match in scan_file(str(file), str(base_dir)):
        result = YaraResult(match)

        template = result.get_template()
        if not template:
            if observer:
                observer.update("Skipping file: %s", rel_path, do_log=True)
            else:
                logger.debug("Skipping file: %s", rel_path)
            continue

        snippet = Snippet.objects.create(
            language=result["language"],
            file_name=File.relative_path(result.target),
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


def yara_code_analysis(
    scan_task_pk: str,
    start_dir: str,
    observer: Observer = None,
    base_dir: str = YARA_BASE_DIR,
):
    if observer:
        observer.update(
            "Started YARA Code analysis...", do_log=True, log_level=logging.INFO
        )

    task = ScanTask.objects.get(pk=scan_task_pk)
    path = pathlib.Path(start_dir)
    if not path.exists():
        (logger if not observer else observer.logger).warning(
            "Could not validate start directory: %s", File.relative_path(path)
        )
    else:
        total = 100
        if observer:
            # Extra: use this function in your shared task and track the current progress
            # of this scan.
            observer.pos = 0
            observer.update("Enumerating file objects...", do_log=True)
            total = len(list(path.glob("*/**")))
            observer.update("Starting YARA Scan...", total=total, do_log=True)

        for directory in path.glob("*/**"):
            # Reset the progres bar if
            if observer:
                observer.update(
                    "Scanning folder: `%s` ...",
                    File.relative_path(directory),
                    do_log=True,
                    total=total,
                )

            if not mp.current_process().daemon:
                with mp.Pool(os.cpu_count()) as pool:
                    pool.starmap(
                        yara_scan_file,
                        [
                            (child, task, base_dir)
                            for child in directory.iterdir()
                            if not child.is_dir()
                        ],
                    )
            else:
                # As we can't use sub processes in a daemon process, we have to
                # call the function with a ThreadPoolExecutor
                with ThreadPoolExecutor() as executor:
                    for child in directory.iterdir():
                        if child.is_dir():
                            continue
                        # observer.update("Scanning file: <%s> ...", str(child.name), do_log=True, total=total)
                        executor.submit(yara_scan_file, child, task, base_dir)

