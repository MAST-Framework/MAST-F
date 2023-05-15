import logging
import pathlib
import inspect
import re

from mastf.core.progress import Observer
from mastf.core.code import yara_code_analysis

from mastf.MASTF.scanners.mixins import (
    DetailsMixin,
    PermissionsMixin,
    HostsMixin,
    FindingsMixins,
    ComponentsMixin,
)
from mastf.MASTF.scanners.plugin import Plugin, ScannerPlugin, Extension
from mastf.MASTF.models import Scan, ScanTask

from mastf.MASTF.scanners.android_sast import run_manifest_scan

logger = logging.getLogger(__name__)


class AndroidScanner:
    def __init__(self) -> None:
        self._task = None
        self._observer = None
        self._file_dir = None

    def __call__(self, scan: Scan, task: ScanTask, observer: Observer) -> None:
        self._task = task
        self._observer = observer

        # run mp on all manifests that can be read
        project = scan.project
        self._file_dir = project.dir(scan.file.internal_name, False)

        for name, func in inspect.getmembers(self):
            if name.startswith("do"):
                self.observer.update(
                    "Started sub-task %s",
                    "-".join([x.capitalize() for x in name.split("-")[1:]]),
                    do_log=True,
                    log_level=logging.INFO
                )
                func()

    @property
    def scan_task(self) -> ScanTask:
        return self._task

    @property
    def file_dir(self) -> pathlib.Path:
        return self._file_dir

    @property
    def observer(self) -> Observer:
        return self._observer

    def do_yara_scan(self) -> None:
        yara_code_analysis(self.scan_task.pk, str(self.file_dir), self.observer)

    def do_manifest_scan(self) -> None:
        content_dir = self.file_dir / "contents"
        manifest_files = content_dir.glob("AndroidManifest.xml")

        self.observer.update("Running manifest analysis...", do_log=True)
        for manifest in manifest_files:
            run_manifest_scan(self.scan_task, manifest, self.observer)


mixins = (DetailsMixin, PermissionsMixin, HostsMixin, FindingsMixins, ComponentsMixin)


@Plugin
class AndroidScannerPlugin(*mixins, ScannerPlugin):
    name = "Android Plugin"
    title = "Android SAST Engine"
    help = "Basic security checks for Android apps."
    task = AndroidScanner
    extensions = [
        Extension.DETAILS,
        Extension.PERMISSIONS,
        Extension.HOSTS,
        Extension.FINDINGS,
        Extension.EXPLORER,
        Extension.COMPONENTS,
    ]
