from __future__ import annotations

from io import IOBase, StringIO, BytesIO

GROUP_TYPE = "group:"
UNGROUPED_TYPE = "ungrouped"
PERMISSION_TYPE = "permission:"


def parse(text: str | bytes | IOBase = None) -> _APL:
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


def load(fp: IOBase) -> _APL:
    instance = _APL()
    current_group = instance.ungrouped
    current = None

    for line in iter(lambda: fp.readline(), 0):
        if isinstance(line, (bytes, bytearray)):
            line = line.decode()

        cleaned = line.strip()
        if len(cleaned) == 0:
            continue

        if cleaned[0] == "+":
            identifier = cleaned[1:].strip()
            if identifier.startswith(GROUP_TYPE):
                current_group = {}
                current = None
                instance[identifier.lstrip(GROUP_TYPE)] = current_group

            elif identifier == UNGROUPED_TYPE:
                current = None
                current_group = instance.ungrouped

            elif identifier.startswith(PERMISSION_TYPE):
                current = {}
                if current_group == instance.ungrouped:
                    current_group[identifier.lstrip(PERMISSION_TYPE)] = current
                else:
                    if "permissions" not in current_group:
                        current_group["permissions"] = {}


        elif current_group and current_group != instance.ungrouped or current:
            target = current_group if not current else current
            name, value = line.split(":", 1)
            if name.lower() == "protectionlevel":
                target[name] = value.split("|") if value != "null" else None
            else:
                target[name] = value if value != "null" else None


class _APL:
    def __init__(self) -> None:
        self.__groups = {}
        self.__permissions = {}

    @property
    def ungrouped(self) -> dict:
        return self.__permissions

    def __contains__(self, key: str) -> bool:
        return key in self.__groups

    def __getitem__(self, key: str) -> dict:
        return self.__groups[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.__groups[key] = value

    def __iter__(self):
        return iter(self.__groups)