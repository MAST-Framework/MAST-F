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
__doc__ = """
The ``mastf.android.permission.adb`` module provides a utility class that
facilitates the parsing and utilization of ADB (Android Debug Bridge) output
related to device permissions. This module offers convenient functionality to
extract and work with permissions information obtained from an Android device
using ADB commands.

This documentation provides an overview of the utility class and its capabilities.
The :class:`AndroidPermissions` class is specifically designed to parse and process
the output of ADB commands related to permissions on Android devices. It simplifies
extraction of permission details, allowing developers to access and utilize permission-
related information programmatically.

Key Features
~~~~~~~~~~~~

1. Permission Output Parsing:

    The :class:`AndroidPermissions` class handles the parsing of ADB output related to
    permissions. It can extract relevant information such as permission names, informational
    labels, and protection levels.

2. Accessible Permission Data:

    Once the ADB output is parsed, the utility class provides convenient methods to access
    permission-related data in a structured format. This enables developers to retrieve and
    manipulate permission information for further analysis or integration with other processes.

3. Simplified Import/Export:

    By extending the inbuilt dictionary class, you can simply export an instance of the
    :class:`AndroidPermissions` to JSON format.

Import Format
~~~~~~~~~~~~~

The ADB output for a device's permissions consists of a structured format that provides information
about individual permissions, including their names, associated packages, labels, descriptions, and
protection levels. The following specification outlines the structure and attributes of the ADB
output:

1. Format:

    * The ADB output is represented in a hierarchical structure with indentation for readability.
    * Each permission and group entry is preceded by a "+", and the indentation level indicates the hierarchy.

2. Group Entry: (*suffix =* ``group:``)

    * Groups must be specified before simple permissions are written.
    * They can store labels as defined in permission entries and permissions as well

3. Permission Entry:

    * Each permission entry represents a specific permission and its associated details.
    * It contains the following attributes:

        - ``permission``: The name of the permission.

        - ``package``: The package name of the app associated with the permission.

        - ``label``: The label or name of the permission (if available).

        - ``description``: The description or purpose of the permission (if available).

        - ``protectionLevel``: The protection level of the permission (e.g., normal, dangerous, etc.).

4. Example:

    An example ADB output for a device's permissions:

    .. code-block:: text
        :linenos:

        + ungrouped:
            + permission:com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE
                package:com.android.vending
                label:Play Install Referrer API
                description:Allows the app to retrieve its install referrer information.
                protectionLevel:normal
            + permission:com.samsung.android.mapsagent.permission.READ_APP_INFO
                package:com.samsung.android.mapsagent
                label:null
                description:null
                protectionLevel:normal
"""
import re
import subprocess

from io import IOBase, StringIO, BytesIO


GROUP_TYPE = "group:"
UNGROUPED_TYPE = "ungrouped"
PERMISSION_TYPE = "permission:"


class AndroidPermissions(dict):
    """Management class to store all android permissions of an Android device.

    This class will provide different results according to the used options
    within initialization. There are the following default options:

    - ``package``: Specifies a regular expression to filter the result of ADB
    - ``text``: instead of using the ADB command line utility, the text that should be imported/ parsed can be provided by using this parameter.
    - ``adb_path``: Enables this class to use another ADB path
    - ``group``: Groups all permissions by their permission group
    - ``dangerous``: Lists only permissions that are dangerous
    - ``invisible``: Lists permissions that are invisible to the user by default (will be ignored by default)

    The returned permission and permission-group will have the following structure:

    >>> AndroidPermissions.all()
    { \n\
        "identifier": {\n\
            "label": "value" or None or ['protectionLevel1', ...] \n\
        } \n\
    }

    """

    kwargs: dict
    """Additional arguments that should be covered when importing permissions"""

    re_package: re.Pattern = re.compile(r".*")
    """Regex to filter out unnecessary permissions or groups"""

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        re_pkg = self.kwargs.pop("package", None)
        if re_pkg:
            self.re_package = re.compile(re_pkg)

    @property
    def ungrouped(self) -> dict:
        """Returns all permissions that don't belong to any group

        :return: all ungrouped permissions or this instance of no groups are present
        :rtype: dict
        """
        if self.kwargs.get("group", False):
            return self.get("ungrouped", UNGROUPED_TYPE)
        return self

    @staticmethod
    def all(**kwargs) -> "AndroidPermissions":
        """Returns all Android permissions of a device

        :return: all permissions mapped into JSON objects
        :rtype: AndroidPermissions
        """
        text = kwargs.pop("text", None)

        permissions = AndroidPermissions(**kwargs)
        permissions.load(text)
        return permissions

    def load(self, text: str = None) -> None:
        """Imports the permissions from the given text or vie ADB

        :param text: the permissions to import, defaults to None
        :type text: str, optional
        :raises TypeError: if the text type is invalid
        """
        if text is not None:
            if isinstance(text, (bytearray, bytes)):
                source = BytesIO(text)
            elif isinstance(text, str):
                source = StringIO(text)
            elif isinstance(text, IOBase):
                source = text
            else:
                raise TypeError(f"Invalid source type: {type(text)}")

        else:
            # The command depends on the provided arguments
            cmd = self.make_cmd()
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, check=True
                )
                source = BytesIO(result.stdout)
            except subprocess.CalledProcessError as err:
                # By re-raising this exception the output will provide more details
                raise RuntimeError(err.stderr.decode()) from err

        assert source, "The input source must not be null!"
        self._parse(source)

    def make_cmd(self) -> str:
        """Generates the ADB shell command used to fetch all permissions

        :return: the generated command
        :rtype: str
        """
        adb_path = self.kwargs.get("adb_path", "adb")
        args = []
        if self.kwargs.get("group", False):
            args.append("-g")
        if self.kwargs.get("dangerous", False):
            args.append("-d")
        if not self.kwargs.get("invisible", False):
            args.append("-u")
        return f"{adb_path} shell pm list permissions -f {' .'.join(args)}"

    def _parse(self, text: IOBase) -> None:
        parent = None
        element = None
        while True:
            line = text.readline()
            if len(line) == 0:
                break

            line = line.strip()
            if len(line) == 0:
                continue

            if isinstance(line, (bytes, bytearray)):
                line = line.decode()

            assert isinstance(line, str), "The input line must be of type string"

            if line[0] == "+":  # permission or group definition
                identifier = line[1:].strip()
                if identifier.startswith(GROUP_TYPE) or identifier == UNGROUPED_TYPE:
                    identifier = identifier.lstrip(GROUP_TYPE)
                    if self.re_package.match(identifier):
                        parent = {}
                        element = None
                        self[identifier] = parent

                elif identifier.startswith(PERMISSION_TYPE):
                    element = {}
                    identifier = identifier.lstrip(PERMISSION_TYPE)
                    if self.re_package.match(identifier):
                        if (
                            parent is not None
                        ):  # maps the given permission element to a group
                            parent[identifier] = element
                        else:
                            self[identifier] = element

            elif parent is not None or element is not None:
                val: dict = parent if element is None else element
                name, desc = line.split(":")
                if name.lower() == "protectionlevel":
                    val[name] = desc.split("|") if desc != "null" else []
                else:
                    val[name] = desc if desc != "null" else None
