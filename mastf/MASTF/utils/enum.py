from enum import Enum

class StringEnum(Enum):
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return __value == self.value
        return super().__eq__(__value)

    def __ne__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.value != __value
        return super().__ne__(__value)

    def __str__(self) -> str:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)

class Severity(StringEnum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"
    SECURE = "Secure"
    NONE = "None"

class State(StringEnum):
    TO_VERIFY = "To Verify"
    CONFIRMED = "Confirmed"
    URGENT = "Urgent"
    NOT_EXPLOITABLE = "Not Exploitable"
    PROPOSED_NOT_EXPLOITABLE = "Proposed not exploitable"

class Visibility(StringEnum):
    PUBLIC = "Public"
    PRIVATE = "Private"
    INTERNAL = "Internal"

class InspectionType(StringEnum):
    SIMPLE = "Simple"
    ADVANCED = "Advanced"

class Platform(StringEnum):
    ANDROID = "Android"
    IOS = "iOS"
    UNKNOWN = "Undefined"

class PackageType(StringEnum):
    GITHUB = "Github"
    DART = "Dart"
    CORDOVA = "Cordova"
    FLUTTER = "Flutter"
    NONE = "None"


class Relation(StringEnum):
    TRANSITIVE = 'Transitive'
    DIRECT = 'Direct'

for cls in (PackageType, Visibility, Severity, Platform, InspectionType,
            Relation):
    setattr(cls, 'choices', [(str(x), str(x)) for x in cls])
