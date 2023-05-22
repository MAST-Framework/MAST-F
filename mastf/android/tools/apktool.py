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
Support for apktool to be called within Python code. Use this module
to extract sources or resources separately or extract an APK file
completely.
"""
import subprocess


def extractrsc(apk_path: str, dest_path: str, apktool_path: str = "apktool") -> None:
    """Extracts only resources from an APK file.

    :param apk_path: The path to the APK file to decode.
    :type apk_path: str
    :param dest_path: The path to the directory where the decoded files will be placed.
    :type dest_path: str
    :param apktool_path: The path to the apktool executable. Defaults to "apktool".
    :type apktool_path: str, optional
    """
    run_apktool_decode(apk_path, dest_path, apktool_path, force=True, sources=False)


def run_apktool_decode(
    apk_path: str,
    dest_path: str,
    apktool_path: str = "apktool",
    force: bool = True,
    sources: bool = True,
    resources: bool = True,
) -> None:
    """
    Decodes the specified APK file using apktool.

    :param apk_path: The path to the APK file to decode.
    :type apk_path: str
    :param dest_path: The path to the directory where the decoded files will be placed.
    :type dest_path: str
    :param apktool_path: The path to the apktool executable. Defaults to "apktool".
    :type apktool_path: str, optional
    :param force: Whether to force overwrite existing files. Defaults to True.
    :type force: bool, optional
    :param sources: Whether to decode sources. Defaults to True.
    :type sources: bool, optional
    :param resources: Whether to decode resources. Defaults to True.
    :type resources: bool, optional
    :raises RuntimeError: If apktool fails to decode the APK file.
    """
    cmd = [f"{apktool_path} d {apk_path} -o {dest_path}"]
    if force:
        cmd.append("-f")

    if not sources:
        cmd.append("--no-src")

    if not resources:
        cmd.append("--no-res")

    try:
        subprocess.run(" ".join(cmd), shell=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        # Raise a RuntimeError if apktool fails to decode the APK file
        raise RuntimeError(err.stdout.decode()) from err
