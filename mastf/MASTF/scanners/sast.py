import re
import pysast
import pathlib

from concurrent.futures import ThreadPoolExecutor

from mastf.core.progress import Observer
from mastf.MASTF.models import Finding, FindingTemplate, Snippet, File, ScanTask


class SastIntegration:
    def __init__(
        self, observer: Observer, rules_dir: str, excluded: list, scan_task: ScanTask
    ) -> None:
        self.observer = observer
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
            if self.scanner.scan(file_path):
                self.observer.update(
                    "Inspecting results of %s", File.relative_path(file_path)
                )
                for match in self.scanner.scan_results:
                    self.add_finding(match)

        except Exception as err:
            self.observer.logger.exception(
                "(%s) Scan failed for %s:", type(err).__name__, file_path
            )
            return False

    def is_excluded(self, path: str) -> bool:
        for val in self.excluded:
            if isinstance(val, re.Pattern) and val.match(path) or val == path:
                return True

    def scan_dir(self, dir_path: pathlib.Path, executor: ThreadPoolExecutor) -> bool:
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and not self.is_excluded(str(file_path)):
                executor.submit(self.scan_file, str(file_path))

    def start(self, target: pathlib.Path) -> None:
        with ThreadPoolExecutor() as executor:
            self.scan_dir(target, executor)

    def add_finding(self, match: dict) -> None:
        internal_id = match[pysast.RESULT_KEY_META].get("template")
        template = FindingTemplate.objects.filter(internal_id=internal_id)
        if not template.exists():
            self.observer.logger.error(
                "Could not find template '%s' for rule '%s'!",
                internal_id,
                match[pysast.RESULT_KEY_RULE_ID],
            )
            return

        path = pathlib.Path(match[pysast.RESULT_KEY_ABS_PATH])
        template = template.first()
        snippet = Snippet.objects.create(
            lines=",".join(match[pysast.RESULT_KEY_LINES]),
            language=path.suffix,
            file_name=path.stem,
            sys_path=str(path),
        )
        Finding.objects.create(
            finding_id=Finding.make_uuid(),
            scan=self.scan_task.scan,
            scanner=self.scan_task.scanner,
            snippet=snippet,
            template=template,
            severity=match[pysast.RESULT_KEY_META].get(
                "severity", template.default_severity
            ),
            custom_text=match[pysast.RESULT_KEY_META].get("text"),
        )