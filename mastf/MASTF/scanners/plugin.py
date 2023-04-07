from abc import ABCMeta


from mastf.MASTF.models import (
    Project, ProjectScanner, Scan, File
)

from . import extensions

__scanners__ = {}

def Plugin(clazz):
    clazz()
    return clazz

    

class ScannerPlugin(metaclass=ABCMeta):

    name: str = None
    """The name (slug) of this scanner type (should contain no whitespace characters)"""

    help: str = None
    """The help that will be displayed on the WebUI"""

    title: str = None
    """Actual name (more details than ``name``)"""

    extensions: list = []
    
    task = None
    """The task to perform asynchronously"""

    def __init__(self) -> None:
        if not self.name:
            raise ValueError("The scanner's name can not be null!")

        if self.name in __scanners__:
            raise KeyError("Scanner already registered")

        self._internal = self.name.lower().replace(' ', "-").replace('--', '-')
        __scanners__[self._internal] = self

    def context(self, extension: str, project: Project, file: File) -> dict:
        """Generates the rendering context for the given extension

        :param extension: the extension to render
        :type extension: str
        :return: the final context
        :rtype: dict
        """
        
        func_name = f"ctx_{extension}"
        if hasattr(self, func_name):
            return getattr(self, func_name)(project, file)
        
        return {}

    def results(self, extension: str, scan: Scan) -> dict:
        func_name = f"res_{extension}"
        if hasattr(self, func_name):
            return getattr(self, func_name)(scan)
        
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
        
        for key, value in __scanners__.items():
            if ProjectScanner.objects.filter(name=key, project=project).exists():
                result[key] = value
        return result


# TEST: The scanner implements all context functions in 
# order to test the functionality of scanner pages.
from mastf.MASTF.scanners.mixins import *
@Plugin
class TestScanner(DetailsMixin, VulnerabilitiesMixin,
                  PermissionsMixin, FindingsMixins,
                  ScannerPlugin):
    extensions = [
        extensions.EXT_DETAILS,
        
        extensions.EXT_PERMISSIONS,
        extensions.EXT_HOSTS,
        extensions.EXT_VULNERABILITIES,
        extensions.EXT_FINDINGS
    ]
    
    name = "Test"
    help = "Basic testing"
    title = "Test Scanner Plugin" 

