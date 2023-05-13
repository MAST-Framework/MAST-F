import multiprocessing as mp
import logging


from mastf.core.progress import Observer
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
    def __call__(self, scan: Scan, task: ScanTask, observer: Observer) -> None:
        # run mp on all manifests that can be read
        project = scan.project

        content_dir = project.dir(scan.file.md5, False) / "contents"
        manifest_files = content_dir.glob("AndroidManifest.xml")

        pool = mp.Pool()
        pool.starmap(run_manifest_scan, [(task, x) for x in manifest_files])


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

