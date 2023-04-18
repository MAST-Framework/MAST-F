import inspect
import sys

class StringConverter:
    def to_python(self, value: str) -> str:
        return value

    def to_url(self, value: str) -> str:
        return value

class FindingTemplateIDConverter(StringConverter):
    regex = r"FT-[\w-]{36}-[\w-]{36}"

class VulnerabilityIDConverter(StringConverter):
    regex = r"SV-[\w-]{36}-[\w-]{36}"

class FindingIDConverter(StringConverter):
    regex = r"SF-[\w-]{36}-[\w-]{36}"

class MD5Converter(StringConverter):
    regex = r"[0-9a-fA-F]{32}"

class HostIDConverter(StringConverter):
    regex = r"host_[\dA-Za-z-]{36}"


def listconverters() -> dict:
    mod = sys.modules[__name__]
    members = inspect.getmembers(mod, inspect.isclass)

    conv = {}
    for name, clazz in members:
        if issubclass(clazz, StringConverter) and clazz != StringConverter:
            name = name.lower().replace('converter', '')
            conv[name] = clazz

    return conv
