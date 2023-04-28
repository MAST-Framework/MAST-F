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

def visitor(is_dir=False, suffix: str = r".*"):
    def wrap(func):
        v = _Visitor(is_dir, re.compile(suffix) if suffix else None, func)
        __visitors__.append(v)
        return func
    return wrap

def _do_visit(file: pathlib.Path, directory_list: list, root_name: str) -> None:
    for visitor in __visitors__:
        matches = visitor.suffix and visitor.suffix.match(file.name)
        path = file.as_posix()

        idx = path.find(root_name)+len(root_name)+1
        common = visitor.common_path and visitor.common_path.match(path[idx:])
        if visitor.is_dir and file.is_dir() and (matches or common):
                visitor.clb(file, directory_list, root_name)
                return

        if matches or common and (not file.is_dir() and not visitor.is_dir):
            visitor.clb(file, directory_list, root_name)
            return

    file_type = "any_type" if not file.is_dir() else "folder"
    path = file.as_posix()
    package_prefix = f"{root_name}/src"
    common = os.path.commonprefix([path[path.find(root_name):], package_prefix])
    if common.startswith(package_prefix) and file.is_dir():
        file_type = "package"

    directory_list.append(_FileDesc(file, file_type, root_name))

def apply_rules(root: pathlib.Path, root_name: str) -> dict:
    data = []

    _do_visit(root, data, root_name)

    if not root.is_dir():
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
