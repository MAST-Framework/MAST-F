import pathlib
import re

from mastf.MASTF import settings

class _Visitor:
    suffix = None
    is_dir = False
    clb = None

__visitors__ = []

def visitor(is_dir=False, suffix: str = r".*"):
    def wrap(func):
        v = _Visitor()
        v.clb = func
        v.is_dir = is_dir
        v.suffix = re.compile(suffix) if suffix else None

        return func
    return wrap


def do_visit(file: pathlib.Path, directory_list: list, is_root=False) -> None:
    for visitor in __visitors__:
        matches = visitor.suffix and visitor.suffix.match(file.name)
        if ((visitor.is_dir and file.is_dir() and matches)
                or (not file.is_dir() and not visitor.is_dir and matches)):
            visitor.clb(file, directory_list, is_root)
            return

    directory_list.append({ "text": file.name, "type": "any_type" if not file.is_dir() else "folder" })


def apply_rules(root: pathlib.Path) -> dict:
    data = []

    do_visit(root, data, is_root=True)

    if not root.is_dir():
        return data.pop()

    children = []
    for file in root.iterdir():
        children.append(apply_rules(file))

    tree = data.pop()
    tree['children'] = children
    return tree

###############################################################################
# DEFAULTS
###############################################################################

class _DefaultVisitor(_Visitor):
    def __init__(self, filetype: str, is_dir=False, suffix=r".*") -> None:
        super().__init__()
        self.is_dir = is_dir
        self.suffix = suffix
        self.filetype = filetype
        self.clb = self.handle

    def handle(self, file: pathlib.Path, children: list, is_root=False) -> None:
        children.append({ "text": file.name, "type": self.filetype })


for filetype, obj in settings.FILE_RULES.items():
    is_dir = obj['is_dir']
    suffix = re.compile(obj['suffix'])
    __visitors__.append(_DefaultVisitor(filetype, is_dir, suffix))
