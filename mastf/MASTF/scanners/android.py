import multiprocessing as mp
import pathlib
from typing import Any

from xml.etree.ElementTree import fromstring

from mastf.core.progress import Observer
from mastf.android.manifest import AXmlVisitor
from mastf.MASTF.scanners.mixins import (
    DetailsMixin,
    PermissionsMixin,
    HostsMixin,
    FindingsMixins,
    ComponentsMixin,
)
from mastf.MASTF.scanners.plugin import Plugin, ScannerPlugin, Extension
from mastf.MASTF.models import Scan, ScanTask

mixins = (DetailsMixin, PermissionsMixin, HostsMixin, FindingsMixins, ComponentsMixin)

class AndroidScanner:

    def __call__(self, scan: Scan, task: ScanTask, observer: Observer) -> Any:
        # run mp on all manifests that can be read
        project = scan.project

        content_dir = project.dir(scan.file.md5, False) / "contents"
        manifest_files = content_dir.glob("AndroidManifest.xml")

        pool = mp.Pool()
        pool.starmap(run_manifest_scan, [(task, x) for x in manifest_files])

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

def run_manifest_scan(task: ScanTask, manifest_file: pathlib.Path):
    visitor = AXmlVisitor()
    handler = AndroidManifestHandler(task)

    if manifest_file.exists():
        try:
            with open(str(manifest_file), "rb") as mfp:
                document = fromstring(mfp)

        except Exception as err:
            # log that
            return

        handler.link(visitor)
        visitor.visit_document(document)



class AndroidManifestHandler:

    def __init__(self, task: ScanTask) -> None:
        self.task: ScanTask = task

    def link(self, visitor: AXmlVisitor) -> None:
        # TODO: link visitor to instance methods
        pass

