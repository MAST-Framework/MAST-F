import re
import pysast
import pathlib

from logging import WARNING, getLogger
from concurrent.futures import ThreadPoolExecutor

from mastf.core.progress import Observer
from mastf.MASTF.models import (
    Finding,
    FindingTemplate,
    Snippet,
    File,
    ScanTask,
    Vulnerability,
)


logger = getLogger(__name__)


class SastIntegration:
    def __init__(
        self, observer: Observer, rules_dir: str, excluded: list, scan_task: ScanTask
    ) -> None:
        self.observer = observer
        self.observer.logger = logger

        self.scan_task = scan_task
        self.scanner = pysast.SastScanner(
            use_mime_type=False, rules_dir=rules_dir, recursive_dir=True
        )
        self.excluded = []
        for val in excluded:
            if val.startswith("re:"):
                self.excluded.append(re.compile(val[3:]))
            else:
                self.excluded.append(val)

    def scan_file(self, file_path: str) -> bool:
        try:
            logger.warning("Starting scan on %s", file_path)

            if self.scanner.scan(file_path):
                for match in self.scanner.scan_results:
                    add_finding(match, self.scan_task)

            return True
        except Exception as err:
            logger.exception(str(err))
            return False

    def is_excluded(self, path: str) -> bool:
        for val in self.excluded:
            if (isinstance(val, re.Pattern) and val.match(path)) or val == path:
                return True

    def scan_dir(
        self, dir_path: pathlib.Path, executor: ThreadPoolExecutor = None
    ) -> bool:
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and not self.is_excluded(str(file_path)):
                logger.info("File-scan submitted: %s", file_path)
                executor.submit(self.scan_file, str(file_path))

    def start(self, target: pathlib.Path) -> None:
        if len(self.scanner.rules) == 0:
            # We don't want to waste time on a scan with no rules.
            self.observer.update(
                "Skipping pySAST scan due to no rules...",
                do_log=True,
                log_level=WARNING,
            )
            return

        # REVISIT: the update() method of an observer should not be called if the
        # target has more than 1000 files.
        self.observer.pos = 0
        self.observer.update(
            "Enumerating file objects...", do_log=True, log_level=WARNING
        )
        total = len(list(target.rglob("*")))

        self.observer.update(
            "Starting pySAST Scan...", total=total, do_log=True, log_level=WARNING
        )
        with ThreadPoolExecutor() as executor:
            self.scan_dir(target, executor)


def add_finding(match: dict, scan_task: ScanTask) -> None:
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
