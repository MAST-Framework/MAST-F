# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import pathlib
import logging
import uuid

from xml.dom.minidom import Element, parse

from mastf.android.axml import AXmlVisitor

from mastf.MASTF.scanners.plugin import ScannerPluginTask
from mastf.MASTF.models import (
    Scan,
    IntentFilter,
    AppPermission,
    PermissionFinding,
    Snippet,
    Component,
    Finding,
    FindingTemplate
)
from mastf.MASTF.utils.enum import ProtectionLevel, Severity, ComponentCategory

logger = logging.getLogger(__name__)


def get_manifest_info(inspector: ScannerPluginTask) -> None:
    """Get manifest information from the Android app.

    This function collects detailed information about permissions, components, and intent filters
    from the AndroidManifest.xml file of the app.

    :param inspector: The scanner plugin task inspector.
    :type inspector: ScannerPluginTask
    """
    inspector.observer.logger = logger
    # Collect detailed information about permissions, components and
    # intent filters
    content_dir = inspector.file_dir / "contents"

    inspector.observer.update("Running manifest analysis...", do_log=True)
    for manifest in content_dir.iterdir():
        if manifest.name == "AndroidManifest.xml":
            run_manifest_scan(
                inspector,
                manifest,
            )


def run_manifest_scan(inspector: ScannerPluginTask, manifest_file: pathlib.Path):
    """
    Run manifest scan on the AndroidManifest.xml file.

    This function parses the AndroidManifest.xml file and performs a scan using the specified
    handler and visitor.

    :param inspector: The scanner plugin task inspector.
    :type inspector: ScannerPluginTask
    :param manifest_file: Path to the AndroidManifest.xml file.
    :type manifest_file: pathlib.Path
    """
    visitor = AXmlVisitor()
    handler = AndroidManifestHandler(inspector, manifest_file)

    if manifest_file.exists():
        try:
            with open(str(manifest_file), "rb") as mfp:
                document = parse(mfp)

            handler.link(visitor)
            visitor.visit_document(document)
        except Exception as err:
            logger.exception(str(err))
            inspector.observer.fail(
                "[%s] Skipping manifest due to parsing error: %s",
                type(err).__name__,
                str(err),
                do_log=True,
                log_level=logging.ERROR,
            )
            return
    else:
        inspector.observer.update(
            "Skipped %s due to non-existed file!", str(manifest_file), do_log=True
        )


class AndroidManifestHandler:
    """Inspects AndroidManifest files.

    :param inspector: The ScannerPluginTask object for scanning.
    :param path: The path to the AndroidManifest.xml file.
    """

    def __init__(self, inspector: ScannerPluginTask, path: pathlib.Path) -> None:
        self.inspector = inspector
        self.path = path
        self.observer = inspector.observer
        self.snippet = Snippet(language="xml", file_name=path.name)
        self._saved = False
        self._application_protected = False

    @property
    def scan(self) -> Scan:
        """
        Returns the scan object associated with the inspector.

        :return: The Scan object.
        """
        return self.inspector.scan

    def link(self, visitor: AXmlVisitor) -> None:
        """
        Links the AndroidManifestHandler with an AXmlVisitor.

        :param visitor: The AXmlVisitor to link with.
        """
        visitor.uses_permission.add("android:name", self.on_permission)

        for name in list(ComponentCategory):
            name = str(name).lower()
            if hasattr(visitor, name):
                getattr(visitor, name).add("android:name", getattr(self, f"on_{name}"))

    def on_permission(self, element: Element, identifier: str) -> AppPermission:
        """
        Event handler for permission elements in the AndroidManifest.xml.

        :param element: The permission element.
        :param identifier: The identifier of the permission.
        """
        queryset = AppPermission.objects.filter(identifier=identifier)

        protection_level = str(
            element.getAttribute("android:protectionLevel") or ""
        ).capitalize()
        if not protection_level:
            protection_level = ProtectionLevel.NORMAL
        else:
            if protection_level not in list(ProtectionLevel):
                self.observer.update(
                    "Switching unknown ProtectionLevel classifier: %s",
                    protection_level,
                    do_log=True,
                )
                protection_level = ProtectionLevel.NORMAL

        if not queryset.exists():
            self.observer.update(
                "Creating new Permission: %s [pLevel=%s]",
                identifier,
                protection_level,
                do_log=True,
            )
            permission = AppPermission.create_unknown(identifier, protection_level)
        else:
            permission = queryset.first()

        if not self._saved:
            self.snippet.save()
            self._saved = True

        finding = PermissionFinding.objects.filter(
            scan=self.scan, permission=permission
        )
        if not finding.exists():
            PermissionFinding.objects.create(
                pk=str(uuid.uuid4()),
                scan=self.scan,
                snippet=self.snippet,
                severity=Severity.MEDIUM if permission.dangerous else Severity.NONE,
                scanner=self.inspector.scan_task.scanner,
                permission=permission,
            )

        return permission

    def _create_finding(self, title: str) -> None:
        _ = FindingTemplate.make_internal_id
        Finding.create(
            FindingTemplate.objects.get(_(title)),
            self.snippet,
            self.inspector.scan_task.scanner,
        )

    def on_application(self, element: Element, name: str) -> None:
        """
        Event handler for application elements in the AndroidManifest.xml.

        :param element: The application element.
        :param name: The name of the application.
        """

        if element.getAttribute("android:usesCleartextTraffic") == "true":
            self._create_finding("AndroidManifest: Clear Text Traffic Enabled")

        if element.getAttribute("android:directBootAware") == "true":
            self._create_finding("AndroidManifest: Direct-Boot Awareness")

        if element.getAttribute("android:debuggable") == "true":
            self._create_finding("Code Security (MSTG-CODE-2): Application Built with Debuggable Flag")

        if element.getAttribute("android:allowBackup") == "true":
            self._create_finding("AndroidManifest: Backup of Application Data allowed")

        if element.getAttribute("android:testOnly") == "true":
            self._create_finding("AndroidManifest: Application in Test-Mode")

    def on_service(self, element: Element, name: str) -> None:
        """
        Event handler for service elements in the AndroidManifest.xml.

        :param element: The service element.
        :param name: The name of the service.
        """
        self.handle_component(element, "service", name)

    def on_provider(self, element: Element, name: str) -> None:
        """
        Event handler for provider elements in the AndroidManifest.xml.

        :param element: The provider element.
        :param name: The name of the provider.
        """
        self.handle_component(element, "provider", name)

    def on_receiver(self, element: Element, name: str) -> None:
        """
        Event handler for receiver elements in the AndroidManifest.xml.

        :param element: The receiver element.
        :param name: The name of the receiver.
        """
        self.handle_component(element, "receiver", name)

    def on_activity(self, element: Element, name: str) -> None:
        """
        Event handler for activity elements in the AndroidManifest.xml.

        :param element: The activity element.
        :param name: The name of the activity.
        """
        self.handle_component(element, "activity", name)

    def handle_component(self, element: Element, ctype: str, name: str) -> None:
        """
        Handles a component element in the AndroidManifest.xml.

        :param element: The component element.
        :param ctype: The component type (e.g., service, provider, receiver).
        :param name: The name of the component.
        """
        component = Component.objects.create(
            cid=Component.make_uuid(),
            scanner=self.inspector.scan_task.scanner,
            name=name,
            category=ctype.capitalize(),
            is_exported=element.getAttribute("android:exported") == "true",
        )
        self.observer.logger.debug("Created component instance %s", component)
        component.save()

        identifier = element.getAttribute("android:permission")
        if identifier:
            component.permission = self.on_permission(element, identifier)

        # TODO: if exported add Finding
        for intent_filter in element.childNodes:
            if intent_filter.nodeName == "intent-filter":
                action = intent_filter.getAttribute("android:name")
                component.intent_filters.add(
                    IntentFilter.objects.create(
                        name=action.split(".")[-1], action=action
                    )
                )
                component.is_main = action == "android.intent.action.MAIN"
                component.is_launcher = action == "android.intent.category.LAUNCHER"

                if not component.is_main and not component.permission and not component.is_exported:
                    # Implicit exported component with or without permission definition
                    # TODO: add findings
                    component.is_protected = False
                    self._create_finding("AndroidManifest: Implicitly Exported App Component")

        if not identifier and not self._application_protected and component.is_exported:
            # Exported component without proper permission declaration
            # TODO: add findings
            component.is_protected = False
            self._create_finding("AndroidManifest: Exported Component without Proper Permission Declaration")

        component.save()
