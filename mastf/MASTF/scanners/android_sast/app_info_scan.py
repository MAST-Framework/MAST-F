from androguard.core.bytecodes import apk

from mastf.MASTF.scanners.plugin import AbstractScanner
from mastf.MASTF.models import (
    Certificate,
    Details,
)


def get_app_info(scanner: AbstractScanner) -> None:
    apk_file: apk.APK = scanner[apk.APK]
    details = Details.objects.get(scan=scanner.scan)

    details.app_name = apk_file.get_app_name()
    details.icon = apk_file.get_app_icon()
    details.app_id = apk_file.get_package()
    details.app_version = apk_file.get_androidversion_name()
    details.target_sdk = apk_file.get_target_sdk_version()

    if apk_file.is_signed():
        for certificate in apk_file.get_certificates():
            version = "v1"
            if certificate.is_signed_v2():
                version = "v2"
            if certificate.is_signed_v3():
                version = "v3"

            cert = Certificate.objects.create(
                version=version,
                sha1=certificate.sha1,
                sha256=certificate.sha256,
                issuer=certificate.issuer.human_friendly,
                subject=certificate.subject.human_friendly,
                hash_algorithm=certificate.hash_algo,
                signature_algorithm=certificate.signature_algo,
                serial_number=certificate.serial_number,
            )
            details.certificates.add(cert)

    details.save()
