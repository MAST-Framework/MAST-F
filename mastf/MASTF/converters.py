
class StringConverter:
    def to_python(self, value: str) -> str:
        return value
    
    def to_url(self, value: str) -> str:
        return value

class FindingTemplateIDConverter(StringConverter):
    regex = r"FT-\w{32}-\w{32}"

class VulnerabilityIDConverter(StringConverter):
    regex = r"SV-\w{32}-\w{32}"

class FindingIDConverter(StringConverter):
    regex = r"SF-\w{32}-\w{32}"
    
class MD5Converter(StringConverter):
    regex = r"[0-9a-fA-F]{32}"
