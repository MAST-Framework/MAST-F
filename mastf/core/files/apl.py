# This file is part of MAST-F's Core API
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
from __future__ import annotations

from io import IOBase, BytesIO, StringIO
from typing import List, Union, Optional
from dataclasses import dataclass, field

GROUP_TYPE = "group:"
UNGROUPED_TYPE = "ungrouped"
PERMISSION_TYPE = "permission:"


@dataclass
class PermissionDefItem:
    """
    Represents a permission definition item.

    :param identifier: Identifier of the permission.
    :param package: Package associated with the permission (optional).
    :param label: Label of the permission (optional).
    :param description: Description of the permission (optional).
    :param protectionLevel: List of protection levels for the permission (default: empty list).
    """

    identifier: str
    package: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    protectionLevel: List[str] = field(default_factory=list)


@dataclass
class GroupDefItem:
    """
    Represents a group definition item.

    :param identifier: Identifier of the group.
    :param package: Package associated with the group (optional).
    :param label: Label of the group (optional).
    :param description: Description of the group (optional).
    :param permissions: List of permissions in the group (default: empty list).
    """

    identifier: str
    package: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    permissions: List[PermissionDefItem] = field(default_factory=list)


@dataclass
class AppPermissionList:
    """
    Represents a list of app permissions.

    :param groups: List of group definitions (default: empty list).
    :param permissions: List of ungrouped permissions (default: empty list).
    """

    groups: List[GroupDefItem] = field(default_factory=list)
    permissions: List[PermissionDefItem] = field(default_factory=list)


def load(fp: IOBase) -> AppPermissionList:
    """
    Load app permission data from a file-like object.

    :param fp: File-like object containing the permission data.
    :return: AppPermissionList object representing the loaded data.
    """

    groups = []
    permissions = []
    current_group = None
    current = None

    for line in iter(lambda: fp.readline(), b""):
        if not line:
            break

        if isinstance(line, (bytes, bytearray)):
            line = line.decode()

        cleaned = line.strip()
        if len(cleaned) == 0:
            continue

        if cleaned[0] == "+":
            identifier = cleaned[1:].strip()

            # Check the identifier type
            if identifier.startswith(GROUP_TYPE):
                current_group = GroupDefItem(identifier.lstrip(GROUP_TYPE))
                current = None
                groups.append(current_group)
            elif identifier.startswith(UNGROUPED_TYPE):
                current = None
                current_group = UNGROUPED_TYPE
            elif identifier.startswith(PERMISSION_TYPE):
                current = PermissionDefItem(identifier.lstrip(PERMISSION_TYPE))

                # Check if the permission belongs to a group or is ungrouped
                if current_group is None or current_group == UNGROUPED_TYPE:
                    permissions.append(current)
                else:
                    current_group.permissions.append(current)

        elif (
            current_group is not None and current_group != UNGROUPED_TYPE
        ) or current is not None:
            target = current_group if current is None else current
            name, value = line.strip().split(":", 1)

            # Set attribute values on the current object
            if hasattr(target, name):
                if name.lower() == "protectionlevel":
                    setattr(target, name, value.split("|") if value != "null" else None)
                else:
                    setattr(target, name, value if value != "null" else None)

    return AppPermissionList(groups, permissions)


def parse(text: Union[str, bytes, IOBase] = None) -> AppPermissionList:
    """
    Parse app permission data from text or a file-like object.

    :param text: Input text or file-like object containing the permission data.
    :return: AppPermissionList object representing the parsed data.
    :raises TypeError: If the input text is None.
    :raises TypeError: If an invalid source type is provided.
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

        return load(source)

    raise TypeError("Got None as input text!")
