import uuid

from androguard.core.bytecodes import apk

from mastf.MASTF import settings
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
    ScannerPluginTask,
)

from mastf.MASTF.tasks import perform_async_sast
from mastf.MASTF.models import ScanTask
from mastf.MASTF.scanners.android_sast import (
    get_manifest_info,
    get_app_info,
    get_app_packages
)


class AndroidTask(ScannerPluginTask):
    """
    Scanner task for performing Android-related scans.

    This task is specifically designed for scanning Android applications and performs various scans
    such as YARA scan, manifest scan, app info scan, and code scan.

    Example:
    ~~~~~~~~

    .. code-block:: python

        android_task = AndroidTask()
        android_task(scan_task, observer)
    """

    def prepare_scan(self) -> None:
        """Prepare the scan by setting up the APK object.

        This method initializes the APK object by loading the APK file associated with the scan.
        """
        self["apk"] = apk.APK(self.scan.file.file_path)

    def do_yara_scan(self) -> None:
        """
        Perform YARA scan on the Android application.

        This method executes the YARA code analysis on the scan task's package directory.
        """
        yara_code_analysis(self.scan_task.pk, str(self.file_dir), self.observer)

    def do_manifest_scan(self) -> None:
        """
        Perform a manifest scan on the Android application.

        This method retrieves the manifest information of the Android application.
        """
        get_manifest_info(self)

    def do_app_info_scan(self) -> None:
        """
        Perform a manifest scan on the Android application.

        This method retrieves the manifest information of the Android application.
        """
        get_app_info(self)

    def do_code_scan(self) -> None:
        """
        Perform a code scan on the Android application.

        This method creates a new scan task and initiates an asynchronous code scan.
        """
        task = ScanTask.objects.create(
            task_uuid=uuid.uuid4(),
            scan=self.scan,
            scanner=self.scan_task.scanner,
            name=self.scan_task.name,
        )
        perform_async_sast.delay(str(task.task_uuid), str(self.file_dir))

    def do_package_scan(self) -> None:
        get_app_packages(self)

mixins = (DetailsMixin, PermissionsMixin, HostsMixin, FindingsMixins, ComponentsMixin)


@Plugin
class AndroidScannerPlugin(*mixins, ScannerPlugin):
    """Android SAST Engine Plugin.

    This scanner plugin provides basic security checks for Android apps. It utilizes
    various mixins for different functionalities such as details, permissions, hosts,
    findings, and components.

    Example:
    ~~~~~~~~

    .. code-block:: python

        android_plugin = AndroidScannerPlugin()
        android_plugin.run_scan()

    .. note::
        Make sure to properly configure the scanner plugin before running the scan.
    """
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
