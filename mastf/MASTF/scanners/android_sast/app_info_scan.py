import logging
import json

from androguard.core.bytecodes import apk

from xml.dom.minidom import Element, parse

from mastf.android.info import get_details
from mastf.android.axml import AXmlVisitor

from mastf.MASTF.scanners.plugin import ScannerPluginTask
from mastf.MASTF.models import (
    Certificate,
    Details,
    File,
    Finding,
    FindingTemplate,
    Snippet,
)

apk.log.setLevel(logging.WARNING)


def get_app_info(inspector: ScannerPluginTask) -> None:
    """Retrieves and saves information about the scanned app.

    :param inspector: The :class:`ScannerPluginTask` object.
    """
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
            if apk_file.is_signed_v2():
                version = "v2"
            if apk_file.is_signed_v3():
                version = "v3"

            details.certificates.add(
                Certificate.objects.create(
                    version=version,
                    sha1=certificate.sha1,
                    sha256=certificate.sha256,
                    issuer=certificate.issuer.human_friendly,
                    subject=certificate.subject.human_friendly,
                    hash_algorithm=certificate.hash_algo,
                    signature_algorithm=certificate.signature_algo,
                    serial_number=certificate.serial_number,
                )
            )

    details.save()
    # TODO: Display information on possible vulnerabilities if application
    # is signed with MD5, SHA1, or v1 signature scheme.

    result = get_details(details.app_id)
    # Create info.json file
    target_path = inspector.file_dir / "info.json"
    if target_path.exists():
        # TODO: log that
        pass

    # The stored app-info file will be used within the scan results tab
    with open(str(target_path), "w") as fp:
        json.dump(result, fp)


def get_app_net_info(inspector: ScannerPluginTask) -> None:
    """
    Retrieve network security information from XML files.

    This function analyzes network_security_config.xml files present in the given directory and its subdirectories,
    extracting network security information from them. The extracted information is processed using a visitor pattern
    implemented by the AXmlVisitor class and a NetworkSecurityHandler.

    :param inspector: An instance of ScannerPluginTask, representing the scanner task.
    :type inspector: ScannerPluginTask
    """
    # # Prepare the directory where the XML files are located
    content_dir = inspector.file_dir / "contents"
    visitor = NetworkSecurityVisitor()
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
            # Log any errors encountered while parsing
            inspector.observer.update(
                "[%s] Skipping network security config due to error: %s",
                type(os_err).__name__,
                str(os_err),
                do_log=True,
                log_level=logging.ERROR,
            )
            continue

        visitor.visit_document(document)


class NetworkSecurityVisitor(AXmlVisitor):
    class Meta:
        exclude = "*"  # excludes all other nodes
        nodes = [  # Custom nodes
            "base-config",
            "domain-config",
            "pin-set",
            "debug-overrides",
        ]


class NetworkSecurityHandler:
    def __init__(self, inspector: ScannerPluginTask) -> None:
        self.inspector = inspector
        self._snippet = None

    def link(self, visitor: AXmlVisitor) -> None:
        visitor.base_config.add(
            "cleartextTrafficPermitted", self.on_base_cfg_cleartext_traffic
        )
        visitor.domain_config.add(
            "cleartextTrafficPermitted", self.on_domain_cfg_cleartext_traffic
        )
        visitor.domain_config.add(
            "cleartextTrafficPermitted", self.on_debug_cfg_cleartext_traffic
        )
        visitor.start.add("base-config", self.on_base_cfg)
        visitor.start.add("domain-config", self.on_domain_cfg)
        visitor.start.add("debug-overrides", self.on_debug_cfg)

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
        self._handle_ct(
            element,
            enabled,
            [
                "base-config-cleartext-traffic-enabled",
                "base-config-cleartext-traffic-disabled",
            ],
        )

    def on_domain_cfg_cleartext_traffic(self, element: Element, enabled: str) -> None:
        self._handle_ct(
            element,
            enabled,
            [
                "domain-config-cleartext-traffic-enabled",
                "domain-config-cleartext-traffic-disabled",
            ],
        )

    def on_debug_cfg_cleartext_traffic(self, element: Element, enabled: str) -> None:
        self._handle_ct(
            element,
            enabled,
            [
                "debug-config-cleartext-traffic-enabled",
                "debug-config-cleartext-traffic-disabled",
            ],
        )

    def on_base_cfg(self, element: Element) -> None:
        self._handle_cfg(
            element,
            [
                "base-config-trust-bundles-certs",
                "base-config-trust-system-certs",
                "base-config-trust-user-certs",
            ],
        )

    def on_domain_cfg(self, element: Element) -> None:
        self._handle_cfg(
            element,
            [
                "domain-config-trust-bundles-certs",
                "domain-config-trust-system-certs",
                "domain-config-trust-user-certs",
            ],
        )

    def on_debug_cfg(self, element: Element) -> None:
        self._handle_cfg(
            element,
            [
                "debug-config-trust-bundles-certs",
                "debug-config-trust-system-certs",
                "debug-config-trust-user-certs",
            ],
        )

    def _handle_ct(self, element, value, templates) -> None:
        template_id = None
        if value == "true":
            template_id = templates[0]
        elif value == "false":
            template_id = templates[1]

        if template_id:
            self.create_finding(FindingTemplate.objects.get(template_id=template_id))

    def _handle_cfg(self, element, templates: list) -> None:
        trust_anchors = element.getElementsByTagName("trust-anchors")
        if trust_anchors:
            template_id = None
            for cert in trust_anchors[0].getElementsByTagName("certifiates"):
                if "@raw/" in cert.getAttribute("src"):
                    template_id = templates[0]
                elif "system" in cert.getAttribute("src"):
                    template_id = templates[1]
                elif "user" in cert.getAttribute("src"):
                    template_id = templates[2]

                if template_id:
                    self.create_finding(
                        FindingTemplate.objects.get(template_id=template_id)
                    )
