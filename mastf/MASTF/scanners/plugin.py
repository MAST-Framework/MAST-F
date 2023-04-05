from abc import ABCMeta
from enum import Enum

from mastf.MASTF.scanners.mixins import DetailsMixin
from mastf.MASTF.models import (
    Project, ProjectScanner, Scan
)

__scanners__ = {}

def Plugin(clazz):
    clazz()
    return clazz

class Extension(Enum):
    EXT_VULNERABILITIES = 'vulnerabilities'
    EXT_PERMISSIONS = 'permissions'
    EXT_DETAILS = 'details'
    EXT_HOSTS = 'hosts'
    EXT_FINDINGS = 'findings'

    def __str__(self) -> str:
        return self.value

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.value == __value
        return super().__eq__(__value)

    def __ne__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.value != __value
        return super().__ne__(__value)


class ScannerPlugin(metaclass=ABCMeta):

    name: str = None
    """The name (slug) of this scanner type (should contain no whitespace characters)"""

    help: str = None
    """The help that will be displayed on the WebUI"""

    title: str = None
    """Actual name (more details than ``name``)"""

    extensions: list = []

    def __init__(self) -> None:
        if not self.name:
            raise ValueError("The scanner's name can not be null!")

        if self.name in __scanners__:
            raise KeyError("Scanner already registered")

        self._internal = self.name.lower().replace(' ', "-").replace('--', '-')
        __scanners__[self._internal] = self

    def context(self, extension: str, project: Project) -> dict:
        """Generates the rendering context for the given extension

        :param extension: the extension to render
        :type extension: str
        :return: the final context
        :rtype: dict
        """
        
        func_name = f"ctx_{extension}"
        if hasattr(self, func_name):
            return getattr(self, func_name)(project)
        
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
@Plugin
class TestScanner(DetailsMixin, ScannerPlugin):
    extensions = [
        Extension.EXT_DETAILS,
        
        Extension.EXT_PERMISSIONS,
        Extension.EXT_HOSTS,
        Extension.EXT_VULNERABILITIES,
        Extension.EXT_FINDINGS
    ]
    
    name = "Test"
    help = "Basic testing"
    title = "Test Scanner Plugin" 

