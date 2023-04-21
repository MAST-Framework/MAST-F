
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
