# This file is part of MAST-F's Android API
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
"""
Wrapper functions for JADX decompiler and dex-tools using subprocess. Note
that these functions are designed to be used within docker containers.
"""
import subprocess
import sys


def getopts(options: list = None) -> str:
    opts = []
    for option in options or []:
        if isinstance(option, str):
            opts.append(option)
        elif isinstance(option, (list, tuple)):
            key, val, *_ = option
            opts.append(f"{key} {val}")

    return " ".join(opts)


def decompile(
    dex_path: str, dest_path: str, baksmali_path: str, options: list = None
) -> None:
    """Decompiles a dex file using Baksmali.

    :param dex_path: The path to the dex file to decompile.
    :type dex_path: str
    :param dest_path: The path to the directory where the decompiled files will be placed.
    :type dest_path: str
    :param baksmali_path: The path to the Baksmali executable.
    :type baksmali_path: str
    :param options: Additional command-line options to pass to Baksmali. Defaults to None.
    :type options: list, optional
    :raises RuntimeError: If Baksmali executable is not found.
    """
    if sys.platform in ("win32", "win64"):
        baksmali_path = f"{baksmali_path}.bat"
    else:
        baksmali_path = f"{baksmali_path}.sh"

    try:
        opts = getopts(options)
        cmd = f"{baksmali_path} {dex_path} -o {dest_path} {opts}"
        subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stdout.decode()) from err


def to_java(dex_dir: str, dex_path: str, dest_path: str, jadx_path: str, options: list = None) -> None:
    """Converts a dex file to Java source code using jadx.

    .. note::
        The extracted files will be placed in the destination directory directly without having
        the extra ``sources/`` directory.

    :param dex_dir: The path to the directory containing the dex file.
    :type dex_dir: str
    :param dex_path: The name of the dex file to convert.
    :type dex_path: str
    :param dest_path: The path to the directory where the Java source files will be placed.
    :type dest_path: str
    :param jadx_path: The path to the jadx executable.
    :type jadx_path: str
    :param options: Additional command-line options to pass to jadx. Defaults to None.
    :type options: list, optional
    :raises RuntimeError: If jadx executable is not found.
    """
    if sys.platform in ("win32", "win64"):
        jadx_path = f"{jadx_path}.bat"

    try:
        cmd = f"cd {dex_dir} && {jadx_path} -d {dest_path} {getopts(options)} {dex_path}"
        subprocess.run(
            f"{cmd} && mv {dest_path}/sources/* {dest_path} && rm -rf {dest_path}/sources",
            shell=True,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(err.stdout.decode()) from err
