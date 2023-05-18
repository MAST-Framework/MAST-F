import logging

from androguard.core.bytecodes import apk

from xml.dom.minidom import Element, parse
from mastf.android.axml import AXmlVisitor

from mastf.MASTF.scanners.plugin import AbstractInspector
from mastf.MASTF.models import (
    Certificate,
    Details,
    File,
    Finding,
    FindingTemplate,
    Snippet,
)


def get_app_info(inspector: AbstractInspector) -> None:
    apk_file: apk.APK = inspector[apk.APK]
    details = Details.objects.get(scan=inspector.scan)

    details.app_name = apk_file.get_app_name()
    details.icon = inspector.file_dir / "contents" / apk_file.get_app_icon()
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


def get_app_net_info(inspector: AbstractInspector) -> None:
    content_dir = scanner.file_dir / "contents"
    visitor = AXmlVisitor()
    handler = NetworkSecurityHandler(inspector)

    handler.link(visitor)
    for net_sec_file in content_dir.glob("*/**/network_security_config.xml"):
        inspector.observer.update(
            "Performing NetworkSecurityConfig Analysis on %s",
            File.relative_path(net_sec_file),
            do_log=True,
            log_level=logging.INFO,
        )

        try:
            with open(str(net_sec_file), "rb") as nfp:
                document = parse(nfp)

        except Exception as os_err:
            inspector.observer.update(
                "[%s] Skipping network security config due to error: %s",
                type(os_err).__name__,
                str(os_err),
                do_log=True,
                log_level=logging.ERROR,
            )
            continue

        visitor.visit_document(document)


class NetworkSecurityHandler:
    def __init__(self, inspector: AbstractInspector) -> None:
        self.inspector = inspector
        self._snippet = None

    def link(self, visitor: AXmlVisitor) -> None:
        pass

    def get_snippet(self) -> Snippet:
        if self._snippet:
            return self._snippet

        scan_file = self.inspector.scan.file
        self._snippet = Snippet.objects.create(
            sys_path=str(scan_file.file_path),
            language="xml",
            file_name=str(scan_file.file_name),
            file_size=scan_file.file_size,
        )

    def create_finding(self, template, msg: str, *args, severity=None) -> Finding:
        return Finding.create(
            template,
            self.get_snippet(),
            self.inspector.scan_task.scanner,
            msg,
            *args,
            severity=severity
        )

    def on_base_cfg_cleartext_traffic(self, element: Element, enabled: str) -> None:
        template_id = None
        if enabled == "true":
            template_id="base-config-cleartext-traffic-enabled"
        elif enabled == "false":
            template_id="base-config-cleartext-traffic-disabled"

        if template_id:
            self.create_finding(FindingTemplate.objects.get(template_id=template_id))
