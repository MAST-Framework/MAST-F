import sys
import inspect

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
    NATIVE = "Native"
    NONE = "None"


class Relation(StringEnum):
    TRANSITIVE = 'Transitive'
    DIRECT = 'Direct'

class HostType(StringEnum):
    INVALID = "Invalid"
    TRACKER = "Tracker"
    OK = "Ok"
    NOT_SET = "Not Set"

class DataProtectionLevel(StringEnum):
    PRIVATE = "Private"
    PUBLIC = "Public"


class ProtectionLevel(StringEnum):
    APP_PREDICTOR = "AppPredictor"
    APPOP = "Appop"
    COMPANION =  "Companion"
    CONFIGURATOR =  "Configurator"
    DANGEROUS =  "Dangerous"
    DEVELOPMENT =  "Development"
    INCIDENTREPORTAPPROVER =  "IncidentReportApprover"
    INSTALLER =  "Installer"
    INSTANT =  "Instant"
    INTERNAL =  "Internal"
    KNOWNSIGNER =  "KnownSigner"
    MODULE =  "Module"
    NORMAL =  "Normal"
    OEM =  "OEM"
    PRE23 =  "Pre23"
    PREINSTALLED =  "Preinstalled"
    PRIVILEGED =  "Privileged"
    RECENTS =  "Recents"
    RETAILDEMO =  "RetailDemo"
    ROLE =  "Role"
    RUNTIME =  "Runtime"
    SETUP =  "Setup"
    SIGNATURE =  "Signature"
    SIGNATUREORSYSTEM =  "SignatureOrSystem"
    SYSTEM =  "System"
    TEXTCLASSIFIER =  "TextClassifier"
    VENDORPRIVILEGED =  "VendorPrivileged"
    VERIFIER =  "Verifier"


    @staticmethod
    def colors() -> dict:
        return {
            'green': (ProtectionLevel.SIGNATURE, ProtectionLevel.SIGNATUREORSYSTEM,
                      ProtectionLevel.KNOWNSIGNER, ProtectionLevel.RUNTIME,
                      ProtectionLevel.DEVELOPMENT, ProtectionLevel.PREINSTALLED),
            'red': (ProtectionLevel.DANGEROUS, ProtectionLevel.SYSTEM, ProtectionLevel.OEM,
                    ProtectionLevel.PRIVILEGED, ProtectionLevel.VENDORPRIVILEGED),
            'azure': (ProtectionLevel.NORMAL, ProtectionLevel.COMPANION, ProtectionLevel.CONFIGURATOR,
                      ProtectionLevel.PRE23)
        }

mod = sys.modules[__name__]
# Small workaround to set an additional static attribute for Django
# models
def isstringenum(member) -> bool:
    return (inspect.isclass(member) and issubclass(member, StringEnum)
        and member.__name__ != 'StringEnum')

for _, clazz in inspect.getmembers(mod, isstringenum):
    setattr(clazz, 'choices', [(str(x), str(x)) for x in clazz])
