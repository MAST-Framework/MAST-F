from androguard.core.bytecodes import apk

from mastf.MASTF.scanners.code import yara_code_analysis
from mastf.MASTF.scanners.mixins import (
    DetailsMixin,
    PermissionsMixin,
    HostsMixin,
    FindingsMixins,
    ComponentsMixin,
)
from mastf.MASTF.scanners.plugin import (
    Plugin,
    ScannerPlugin,
    Extension,
    AbstractInspector,
)

from mastf.MASTF.scanners.android_sast import get_manifest_info, get_app_info


class AndroidTask(AbstractInspector):
    def prepare_scan(self) -> None:
        self["apk"] = apk.APK(self.scan.file.file_path)

    def do_yara_scan(self) -> None:
        yara_code_analysis(self.scan_task.pk, str(self.file_dir), self.observer)

    def do_manifest_scan(self) -> None:
        get_manifest_info(self)

    def do_app_info_scan(self) -> None:
        get_app_info(self)


mixins = (DetailsMixin, PermissionsMixin, HostsMixin, FindingsMixins, ComponentsMixin)


@Plugin
class AndroidScannerPlugin(*mixins, ScannerPlugin):
    name = "Android Plugin"
    title = "Android SAST Engine"
    help = "Basic security checks for Android apps."
    task = AndroidTask
    extensions = [
        Extension.DETAILS,
        Extension.PERMISSIONS,
        Extension.HOSTS,
        Extension.FINDINGS,
        Extension.EXPLORER,
        Extension.COMPONENTS,
    ]
