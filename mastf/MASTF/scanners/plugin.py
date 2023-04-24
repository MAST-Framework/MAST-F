from abc import ABCMeta

from mastf.MASTF.utils.enum import StringEnum
from mastf.MASTF.models import (
    Project, Scanner, Scan, File
)

__scanners__ = {}

def Plugin(clazz):
    clazz()
    return clazz

class Extension(StringEnum):
    DETAILS = "details"
    PERMISSIONS = "permissions"
    HOSTS = "hosts"
    VULNERABILITIES = "vulnerabilities"
    FINDINGS = "findings"
    COMPONENTS = "components"
    EXPLORER = "explorer"

class ScannerPlugin(metaclass=ABCMeta):

    name = None
    """The name (slug) of this scanner type (should contain no whitespace characters)"""

    help = None
    """The help that will be displayed on the WebUI"""

    title = None
    """Actual name (more details than ``name``)"""

    extensions: list = []
    """The list of extensions this scanner supports"""

    task = None
    """The task to perform asynchronously"""

    def __init__(self) -> None:
        if not self.name:
            raise ValueError("The scanner's name can not be null!")

        if self.name in __scanners__:
            raise KeyError("Scanner already registered")

        self._internal = self.name.lower().replace(' ', "-").replace('--', '-')
        __scanners__[self._internal] = self

    def context(self, extension: str, scan: Scan, file: File) -> dict:
        """Generates the rendering context for the given extension

        :param extension: the extension to render
        :type extension: str
        :return: the final context
        :rtype: dict
        """
        scanner = Scanner.objects.filter(scan=scan, name=self.internal_name).first()

        func_name = f"ctx_{extension}"
        if hasattr(self, func_name):
            return getattr(self, func_name)(scan, file, scanner)

        return {}

    def results(self, extension: str, scan: Scan) -> dict:
        scanner = Scanner.objects.filter(scan=scan, name=self.internal_name).first()

        func_name = f"res_{extension}"
        if hasattr(self, func_name):
            return getattr(self, func_name)(scan, scanner)

        return {}

    @property
    def internal_name(self) -> str:
        return self._internal

    @staticmethod
    def all() -> dict:
        return __scanners__

    @staticmethod
    def all_of(project: Project) -> dict:
        result = {}
        if not project:
            return result

        for name in Scanner.names(project):
            result[name] = __scanners__[name]

        return result


# TEST: The scanner implements all context functions in
# order to test the functionality of scanner pages.
from mastf.MASTF.scanners.mixins import *

TextScannerMixins = (DetailsMixin, VulnerabilitiesMixin,
                     PermissionsMixin, FindingsMixins,
                     HostsMixin, ComponentsMixin)

@Plugin
class TestScanner(*TextScannerMixins, ScannerPlugin):
    extensions = [
        Extension.DETAILS,
        Extension.PERMISSIONS,
        Extension.HOSTS,
        Extension.VULNERABILITIES,
        Extension.FINDINGS,
        Extension.EXPLORER,
        Extension.COMPONENTS
    ]

    name = "Test"
    help = "Basic testing"
    title = "Test Scanner Plugin"


