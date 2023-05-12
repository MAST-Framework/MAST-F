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
import re
import pathlib
import zipfile

from mastf.android.tools import apktool, baksmali

handlers = []

class TaskFileHandler:
    def __init__(self, extension: str, scan_type: str = None) -> None:
        if isinstance(extension, type):
            raise ValueError(
                "The provided parameter is of type <class>, expected a string value. "
                "You probably used the @TaskFileHandler decorator without any arguments."
            )

        self.extension = re.compile(extension)
        self.scan_type = scan_type
        self.func = None
        handlers.append(self)

    def __call__(self, *args, **kwargs) -> "TaskFileHandler":
        if len(args) == 0:
            raise ValueError(
                "You called the TaskFileHandler without any arguments, "
                "expected the decorated class or method."
            )

        clazz, *_ = args
        if isinstance(clazz, type):
            clazz = clazz()

        self.func = clazz
        return self

    @staticmethod
    def from_scan(name: str, scan_type: str = None) -> "TaskFileHandler":
        for handler in handlers:
            if handler.extension.match(name) or (
                (handler.scan_type and scan_type) and (handler.scan_type == scan_type)
            ):
                return handler

        return None

    def apply(self, src_path: pathlib.Path, dest_dir: pathlib.Path, settings) -> None:
        if not self.func:
            raise ValueError("Expected a callable function or class instance, got None")

        self.func(src_path, dest_dir, settings)


@TaskFileHandler(extension=r".*\.apk", scan_type="android")
def apk_handler(src_path: pathlib.Path, dest_dir: pathlib.Path, settings):
    src = dest_dir / 'src'
    contents = dest_dir / 'contents'

    apktool.extractrsc(str(src_path), str(contents), settings.APKTOOL)
    smali_dir = src / 'smali'
    smali_dir.mkdir(exist_ok=True)

    tool = f"{settings.D2J_TOOLSET}-dex2smali"
    for path in contents.glob("*.dex"):
        baksmali.decompile(str(path), str(smali_dir), tool)


@TaskFileHandler(extension=r".*\.ipa", scan_type="ios")
def ipa_handler(src_path: pathlib.Path, dest_dir: pathlib.Path, settings) -> None:
    with zipfile.ZipFile(str(src_path)) as zfile:
        # Extract initial files
        zfile.extractall(str(dest_dir / 'contents'))