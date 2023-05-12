# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from abc import ABCMeta

from mastf.MASTF.utils.enum import StringEnum
from mastf.MASTF.models import Project, Scanner, Scan, File

__scanners__ = {}


def Plugin(clazz):
    instance = clazz()
    if not instance.name:
        raise ValueError("The scanner's name can not be null!")

    if instance.name in __scanners__:
        raise KeyError("Scanner already registered")

    instance.internal_name = ScannerPlugin.to_internal_name(instance.name)
    __scanners__[instance.internal_name] = instance
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

    _internal: str = None # noqa

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

    @internal_name.setter
    def internal_name(self, value: str) -> None:
        self._internal = value

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

    @staticmethod
    def to_internal_name(name: str) -> str:
        return str(name).lower().replace(" ", "-").replace("--", "-")
