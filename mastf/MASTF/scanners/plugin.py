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
import inspect
import logging

from abc import ABCMeta
from re import sub
from pathlib import Path


from mastf.core.progress import Observer

from mastf.MASTF.utils.enum import StringEnum
from mastf.MASTF.models import Project, Scanner, Scan, File, ScanTask

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


class AbstractInspector(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._task = None
        self._observer = None
        self._file_dir = None
        self._meta: dict = {}

    def __getitem__(self, key) -> object:
        val = self.get_item(key)
        if not val and key in self._meta:
            return self._meta[key]
        return val

    def __setitem__(self, key, value):
        self._meta[key] = value

    def __call__(self, scan_task: ScanTask, observer: Observer) -> None:
        # Prepare internal values
        self._task = scan_task
        self._observer = observer

        project: Project = scan_task.scan.project
        self._file_dir = project.dir(scan_task.scan.file.internal_name, False)
        self.prepare_scan()
        self.run_scan()

    def get_item(self, key) -> object:
        if isinstance(key, type):
            for value in self._meta.values():
                if isinstance(value, key):
                    return value
        return None

    def prepare_scan(self) -> None:
        pass

    def run_scan(self) -> None:
        for name, func in inspect.getmembers(self):
            if name.startswith("do"):
                name = "-".join([x.capitalize() for x in name.split("_")[1:]])
                self.observer.update(
                    "Started Sub-Task %s", name,
                    do_log=True, log_level=logging.ERROR
                )
                try:
                    func()
                except Exception as err:
                    self.observer.update(
                        "(%s) Sub-Task %s failed: %s",
                        type(err).__name__,
                        name,
                        str(err),
                    )

    @property
    def scan_task(self) -> ScanTask:
        return self._task

    @property
    def scan(self) -> Scan:
        return self._task.scan

    @property
    def file_dir(self) -> Path:
        return self._file_dir

    @property
    def observer(self) -> Observer:
        return self._observer


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

    _internal = None  # noqa

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
        return sub(r"[\s]", "-", str(name)).lower().replace("--", "-")
