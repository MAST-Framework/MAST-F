# This file is part of MAST-F's Frontend API
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

import pysast

from concurrent.futures import ThreadPoolExecutor
from yara_scanner import scan_file

from mastf.core.progress import Observer

from mastf.MASTF.utils.enum import Severity
from mastf.MASTF.settings import YARA_BASE_DIR
from mastf.MASTF.models import (
    Finding,
    FindingTemplate,
    Snippet,
    File,
    ScanTask,
    Vulnerability,
)

logger = logging.getLogger(__name__)


class YaraResult:
    """
    Represents the result of a YARA match.

    This class encapsulates the information extracted from a YARA match and
    provides convenient properties and methods to access and manipulate the
    match data.

    :param match: The dictionary containing the YARA match data.
    """

    def __init__(self, match: dict) -> None:
        self._meta = match["meta"]
        self._severity = None
        self._template = None
        self.target = match["target"]

    @property
    def severity(self) -> Severity:
        """
        Get the severity of the YARA result.

        This property returns the severity of the YARA result. It checks the "severity"
        field in the match metadata and maps it to the corresponding Severity enum value.

        :return: The Severity enum value representing the severity of the result.
        """
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
        """
        Get the ID of the associated finding template.

        This property returns the ID of the associated finding template from the YARA
        match metadata.

        :return: The ID of the finding template.
        """
        return self._meta.get("ft_id", None)

    @property
    def internal_id(self) -> str:
        """
        Get the internal ID of the associated finding template.

        This property returns the internal ID of the associated finding template from
        the YARA match metadata.

        :return: The internal ID of the finding template.
        """
        name = self._meta.get("ft_internal_id", None)
        if not name:
            return name

        return FindingTemplate.make_internal_id(name)

    def get_template_data(self) -> dict:
        """
        Get the data for creating a finding template.

        This method returns a dictionary containing the data required for creating a
        finding template based on the YARA match metadata.

        :return: The data dictionary for creating a finding template.
        """
        return {
            key: self._meta.get(f"ft_fallback_{key}", "")
            for key in ("title", "description", "risk", "mitigation", "article")
        }

    def get_template(self) -> FindingTemplate:
        """
        Get the associated finding template.

        This method retrieves the associated finding template for the YARA result. It
        first checks if a template with the specified ID or internal ID exists. If not,
        it creates a new template using the YARA match metadata.

        :return: The associated FindingTemplate object, or None if it couldn't be
                 retrieved or created.
        """
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
    base_dir=None,
    observer: Observer = None,
):
    """
    Perform YARA scan on a file.

    This function performs YARA scan on the specified file using the YARA rules
    in the given base directory. It creates YaraResult objects for each match
    found and creates corresponding ``Snippet`` and ``Finding`` objects to store
    the scan results.

    :param file: The file path to scan.
    :param task: The ScanTask associated with the scan.
    :param base_dir: The base directory containing the YARA rules.
    :param observer: The observer object for tracking the progress and logging.
    :return: None
    """
    if observer:
        observer.logger = logger

    base_dir = base_dir or YARA_BASE_DIR
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
    base_dir: str = None,
):
    """
    Perform YARA code analysis on files within a directory.

    This function performs YARA code analysis on the files within the specified
    start directory using the provided scan task, base directory, and observer.
    It scans the files in parallel using multiprocessing or a ThreadPoolExecutor
    based on the availability of the current process.

    :param scan_task_pk: The primary key of the ScanTask associated with the code analysis.
    :param start_dir: The directory path where the code analysis will be performed.
    :param observer: The observer object for tracking the progress and logging.
    :param base_dir: The base directory containing the YARA rules.
    :return: None

    Usage:
    ~~~~~~

    .. code-block:: python

        scan_task_pk = "task123"
        start_dir = "/path/to/start_directory"
        observer = Observer()
        base_dir = "/path/to/yara_base_directory"

        yara_code_analysis(scan_task_pk, start_dir, observer, base_dir)
    """
    if observer:
        observer.update(
            "Started YARA Code analysis...", do_log=True, log_level=logging.INFO
        )

    base_dir = base_dir or YARA_BASE_DIR

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


# SAST
def sast_scan_file(
    file_path: pathlib.Path,
    task: ScanTask,
    rules: list,
) -> None:
    """Perform a static application security testing (SAST) scan on a file.

    :param file_path: The path to the file to be scanned.
    :type file_path: pathlib.Path
    :param task: The scan task associated with the file.
    :type task: :class:`ScanTask`
    :param rules: A list of rules to be used for the scan.
    :type rules: list[pysast.SastRule]

    This function performs a SAST scan on the specified file using the provided rules.
    It creates a new instance of the SAST scanner for each scan to ensure that it
    accesses the rules' internal values correctly.

    The scan is performed by calling the ``scan`` method of the scanner instance and
    passing the file path as a string argument. If the scan is successful, the function
    iterates over the scan results and calls the ``add_finding`` function to add each
    finding to the associated scan task.

    If an exception occurs during the scan, the error is logged using the global ``logger``
    instance and the exception is **not** re-raised.
    """
    try:
        # Rather create a new scanner instance every time as it only accesses
        # the rules' internal values
        scanner = pysast.SastScanner(rules=rules, use_mime_type=False)

        if scanner.scan(str(file_path)):
            for match in scanner.scan_results:
                add_finding(match, task)
    except Exception as error:
        logger.exception(str(error))


def sast_code_analysis(
    scan_task: ScanTask,
    target_dir: pathlib.Path,
    observer: Observer,
    excluded: list,
    rules_dirs: list,
) -> None:
    """
    Perform static application security testing (SAST) code analysis on files
    within a target directory.

    This function scans the files within the specified target directory for
    potential security vulnerabilities using the pySAST library. It applies the
    provided scan task, rules directories, and exclusion patterns to determine
    the files to include or exclude from the analysis.

    :param scan_task: The scan task to apply during the code analysis.
    :param target_dir: The directory path where the code analysis will be performed.
    :param observer: The observer object for tracking the progress and logging.
    :param excluded: A list of patterns or regular expressions to exclude specific
                     files or directories from the analysis.
    :param rules_dirs: A list of directories containing the pySAST rules files to
                       use during the analysis.
    :raises FileNotFoundError: If the target directory does not exist.
    :return: None

    Usage:
    ~~~~~~

    .. code-block:: python
        :linenos:

        scan_task = ScanTask(...)
        target_dir = pathlib.Path("/path/to/target/directory")
        observer = Observer(...)
        excluded = ["txt", "re:test_.*"]
        rules_dirs = [pathlib.Path("/path/to/rules/directory")]

        sast_code_analysis(scan_task, target_dir, observer, excluded, rules_dirs)
    """
    # make sure we use the right logger instance
    observer.logger = logger

    if not target_dir.exists():
        # Make sure the task fails by raising an appropriate exception
        raise FileNotFoundError("Could not validate start directory: %s" % target_dir)

    # Prepare excluded values:
    for i, val in enumerate(excluded):
        if val.startswith("re:"):
            excluded[i] = re.compile(val[3:])

    def is_excluded(path: str) -> bool:
        """Check if a file path should be excluded from the analysis.

        :param path: The path of the file to check.
        :return: True if the file should be excluded, False otherwise.
        """
        for val in excluded:
            if (isinstance(val, re.Pattern) and val.match(path)) or val == path:
                return True

    # prepare ruleset
    rules = []
    for directory in rules_dirs:
        for file_path in directory.rglob("*"):
            if pysast.is_rule_file(str(file_path)):
                rules.extend(pysast.load_sast_rules(str(file_path)))

    if len(rules) == 0:
        # We don't want to waste time on a scan with no rules.
        observer.update(
            "Skipping pySAST scan due to no rules...",
            do_log=True,
            log_level=logging.WARNING,
        )
        return

    # REVISIT: the update() method of an observer should not be called if the
    # target has more than 1000 files.
    observer.pos = 0
    observer.update("Enumerating file objects...", do_log=True, log_level=logging.INFO)
    total = len(list(target_dir.glob("*/**")))

    observer.update(
        "Starting pySAST Scan...", total=total, do_log=True, log_level=logging.INFO
    )
    with ThreadPoolExecutor() as executor:
        for directory in target_dir.glob("*/**"):
            observer.update(
                "Scanning folder: `%s` ...",
                File.relative_path(directory),
                do_log=True,
                total=total,
            )
            for child in directory.iterdir():
                if not child.is_file() or is_excluded(str(child)):
                    continue

                executor.submit(sast_scan_file, child, scan_task, rules)


def add_finding(match: dict, scan_task: ScanTask) -> None:
    """Add a finding to the scan task based on the match information.

    This function retrieves the necessary information from the match dictionary
    to create a finding or vulnerability object and associates it with the provided
    scan task.

    The match dictionary contains information about the finding, such as the internal
    ID, rule ID, absolute path, lines, and metadata.

    First, the function extracts the internal ID from the metadata and tries to find
    the corresponding :class`FindingTemplate` object in the database. If the template
    does not exist, an error is logged and the function returns.

    The absolute path is converted to a ``pathlib.Path`` object, and a :class:`Snippet`
    object is created using information from the match dictionary, such as lines,
    language, file name, and system path.

    If the metadata indicates that it is a vulnerability, a :class:`Vulnerability` object
    is created with the corresponding template, snippet, scan, scanner, and severity.
    Otherwise, a Finding object is created.

    :param match: A dictionary containing the match information.
    :type match: dict
    :param scan_task: The scan task to associate the finding with.
    :type scan_task: ScanTask
    """
    internal_id = match[pysast.RESULT_KEY_META].get("template")
    template = FindingTemplate.objects.filter(internal_id=internal_id)
    if not template.exists():
        logger.error(
            "Could not find template '%s' for rule '%s'!",
            internal_id,
            match[pysast.RESULT_KEY_RULE_ID],
        )
        return

    path = pathlib.Path(match[pysast.RESULT_KEY_ABS_PATH])
    template = template.first()
    snippet = Snippet.objects.create(
        lines=",".join(map(str, match[pysast.RESULT_KEY_LINES])),
        language=path.suffix[1:],
        file_name=File.relative_path(str(path)),
        sys_path=str(path),
    )
    meta = match[pysast.RESULT_KEY_META]
    if meta.get("vulnerability", False):
        # Create a vulnerability instead (if not already present)
        Vulnerability.objects.create(
            finding_id=Vulnerability.make_uuid(),
            template=template,
            snippet=snippet,
            scan=scan_task.scan,
            scanner=scan_task.scanner,
            severity=meta.get("severity", template.default_severity),
        )
    else:
        Finding.create(
            template,
            snippet,
            scan_task.scanner,
            severity=meta.get("severity", template.default_severity),
            text=meta.get("text"),
        )
