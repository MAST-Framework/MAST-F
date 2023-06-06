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

import io


class Properties:
    """
    A class for loading and managing properties from a file or IO stream.

    The Properties class provides methods to load properties from a file or IO stream.
    It supports key-value pairs separated by a separator character and allows comments.
    The loaded properties can be accessed using dictionary-like syntax or specific methods.

    :param fp: File path or IO stream to load the properties from., defaults to None
    :type fp: str | io.IOBase, optional
    :param sep: Separator character between keys and values. Default is ``'='``.
    :type sep: str, optional
    :param comment: Character indicating a comment. Default is ``'#'``.
    :type comment: str, optional

    Examples:
    ~~~~~~~~

    .. code-block:: python
        :linenos:

        # Create a Properties instance and load properties from a file
        props = Properties('config.properties')

        # Access properties using dictionary-like syntax
        value = props['key']
        props['key'] = 'new_value'

        # Get property value with a default fallback
        value = props.get('key', 'default_value')

        # Get the set of all keys
        keys = props.keys

        # Get a list of all values
        values = props.values

        # Check if a key exists
        if 'key' in props:
            ...
    """

    def __init__(
        self, fp: str | io.IOBase = None, sep: str = None, comment: str = None
    ) -> None:
        self.__values = {}
        self.separator = sep or "="
        self.comment = comment or "#"
        if fp:
            self.load(fp)

    def load(self, fp: str | io.IOBase) -> None:
        """Load properties from a file or IO stream.

        :param fp: File path or IO stream to load the properties from.
        :type fp: str | io.IOBase
        """
        if isinstance(fp, io.IOBase):
            self._load(fp, self.separator, self.comment)
        elif isinstance(fp, str):
            with open(fp, "rb") as res:
                self._load(res, self.separator, self.comment)

    def _load(self, res: io.IOBase, sep="=", comment="#") -> None:
        """Internal method to load properties from an IO stream.

        :param res: IO stream to load the properties from.
        :type res: io.IOBase
        :param sep: Separator character between keys and values, defaults to "="
        :type sep: str, optional
        :param comment: Character indicating a comment, defaults to "#"
        :type comment: str, optional
        """
        line = res.readline()
        while line:
            if isinstance(line, (bytearray, bytes)):
                line = line.decode()

            cleaned = line.strip()
            if cleaned and not cleaned.startswith(comment) and sep in cleaned:
                key, value = cleaned.split(sep, 1)
                # TODO: handle EOL comments
                self.__values[key.strip()] = value.strip().strip('"')

            line = res.readline()

    def get(self, key, __default=None) -> str:
        """Gets the value of a property.

        :param key: Key of the property.
        :type key: str
        :param __default: Default value if the key does not exist, defaults to None
        :type __default: Any, optional
        :return: Value of the property if found, otherwise the default value
        :rtype: str
        """
        return self.__values.get(key, __default)

    @property
    def keys(self) -> set[str]:
        """Returns all property keys.

        :return: the imported property keys
        :rtype: set[str]
        """
        return set(self.__values.keys())

    @property
    def values(self) -> list[str]:
        """All values of this properties instance.

        :return: a list of values
        :rtype: list[str]
        """
        return list(self.__values.values())

    def __getitem__(self, key: str) -> str:
        return self.__values[key]

    def __setitem__(self, key: str, value: str):
        self.__values[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.__values
