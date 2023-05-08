# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor, Janbehere1
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
Simple visitor API used to generate source trees that can be applied to the
`jsTree <https://www.jstree.com/>`_ javascript plugin.

All classes of this module should be treated as internal. However, if you
want to include a new visitor, there are two ways to implement it:

1. Define a python function that inserts necessary data:

    .. code-block:: python
        :linenos:

        from mastf.MASTF.utils.filetree import visitor

        @visitor(suffix=r".*\.(txt)$")
        def visit_txt(file: pathlib.Path, children: list, root_name: str):
            ... # handle file and add the item to the children list

2. Insert a new JSON structure to `/mastf/json/filetypes_rules.json`:

    .. code-block:: python

        {
            # ...
            "{name}": {
                "is_dir": False,
                "suffix": "{pattern}",
                "language": "{language}"
            }
            # ...
        }

    Whereby ``name`` corresponds to a SVG file with the same name stored in
    ``/mastf/static/static/filetypes/``. Use a pattern within the ``suffix``
    variable to apply your filter to more than just one file type. The specified
    language will be used when showing the file in the web frontend.
"""

import pathlib
import re
import os

from mastf.MASTF import settings

__all__ = [
    'apply_rules', 'visitor'
]

class _Visitor:
    """Internal visitor class used to add the files internally.

    Each instance stores the RegEx pattern to identify a file
    matching a given ruleset. Additionally, a callback function
    is defined that will be called whenever the pattern is
    matched.
    """

    suffix = None
    """The RegEx pattern to identify a specific file set."""

    is_dir = False
    """Tells the internal algorithm to match only directories with
    the pattern."""

    clb = None
    """The callback function with the following structure:


    >>> def function(file: pathlib.Path, children: list, root_name: str):
    ...     pass
    >>> clb = function
    """

    common_path = None
    """
    Common path can be used to apply filters according to the common
    base path.
    """

    def __init__(self, is_dir: bool, suffix: str, clb) -> None:
        self.suffix = re.compile(suffix) if suffix else None
        self.is_dir = is_dir
        self.clb = clb

class _FileDesc(dict):
    """Internal wrapper class to create JSTree JSON data."""

    def __init__(self, file: pathlib.Path, file_type: str, root_name: str, language: str=None):
        super().__init__()
        path = file.as_posix()

        self['text'] = file.name
        self['type'] = file_type
        self['li_attr'] = {
            # The relative path is needed when fetching file information
            # and the directory indicator is used within the JavaScript
            # code.
            "path": path[path.find(root_name):],
            "is-dir": file.is_dir(),
            "file-type": file_type
        }
        if language:
            self['li_attr']['language'] = language

__visitors__ = []
"""Internal visitor list storing all registered visitors."""

def visitor(is_dir=False, suffix: str = r".*"):
    """Creates a new visitor by wrapping the underlying function

    :param is_dir: describes whether the visitor applies to directories, defaults
                   to False
    :type is_dir: bool, optional
    :param suffix: pattern for files, defaults to ``r".*"``
    :type suffix: str, optional
    """
    def wrap(func):
        v = _Visitor(is_dir, re.compile(suffix) if suffix else None, func)
        __visitors__.append(v)
        return func
    return wrap

def _do_visit(file: pathlib.Path, children: list, root_name: str) -> None:
    # Iterates over a list of registered visitor objects.
    for visitor in __visitors__:
        # Matches file names and paths with visitor objects and returns the common path
        # between them.
        matches = visitor.suffix and visitor.suffix.match(file.name)
        path = file.as_posix()

        idx = path.find(root_name)+len(root_name)+1
        common = visitor.common_path and visitor.common_path.match(path[idx:])
        if visitor.is_dir and file.is_dir() and (matches or common):
            # If the file object matches the visitor's suffix or common path and the file
            # object is not a directory, then execute the visitor's callback function on
            # the file object and add it to the children list.
            visitor.clb(file, children, root_name)
            return

        if matches or common and (not file.is_dir() and not visitor.is_dir):
            # If the visitor object watches on directories and the file object is also a
            # directory, then execute the visitor's callback function on the file object
            # and add it to the children list.
            visitor.clb(file, children, root_name)
            return

    # Determines the type of the file object by checking if it's a directory or
    # a file. If it's a directory, the function checks if the file object is in
    # a package directory by comparing its path with the package prefix. If so,
    # it sets the file type as "package".
    file_type = "any_type" if not file.is_dir() else "folder"
    path = file.as_posix()
    package_prefix = f"{root_name}/src"
    common = os.path.commonprefix([path[path.find(root_name):], package_prefix])
    if common.startswith(package_prefix) and file.is_dir():
        file_type = "package"

    children.append(_FileDesc(file, file_type, root_name))

def apply_rules(root: pathlib.Path, root_name: str) -> dict:
    """Applies loaded rules to the given file path.

    :param root: the root file
    :type root: pathlib.Path
    :param root_name: the root node's name (may differ from file name)
    :type root_name: str
    :return: a dictionary that can be used within jsTree definitions
    :rtype: dict
    """
    data = []
    _do_visit(root, data, root_name)
    if not root.is_dir():
        # Only one children present
        return data.pop()

    children = []
    for file in root.iterdir():
        children.append(apply_rules(file, root_name))

    tree = data.pop()
    tree['children'] = children
    return tree

###############################################################################
# DEFAULTS
###############################################################################

class _DefaultVisitor(_Visitor):
    def __init__(self, filetype: str, is_dir=False, suffix=r".*", language=None) -> None:
        super().__init__(is_dir, suffix, self.handle)
        self.filetype = filetype
        self.language = language or 'text'

    def handle(self, file: pathlib.Path, children: list, root_name: str) -> None:
        children.append(_FileDesc(file, self.filetype, root_name, self.language))

for filetype, obj in settings.FILE_RULES.items():
    is_dir = obj.get('is_dir', False)
    suffix = obj.get('suffix', None)
    common_path = obj.get('common_path', None)
    lang = obj.get('language', None)

    v = _DefaultVisitor(filetype, is_dir, suffix, lang)
    v.common_path = re.compile(common_path) if common_path else None
    __visitors__.append(v)
