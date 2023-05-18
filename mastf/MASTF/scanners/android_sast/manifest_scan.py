import pathlib
import logging
import uuid

from xml.dom.minidom import Element, parse

from mastf.android.manifest import AXmlVisitor
from mastf.core.progress import Observer

from mastf.MASTF.scanners.plugin import AbstractScanner
from mastf.MASTF.models import (
    Scan,
    IntentFilter,
    AppPermission,
    PermissionFinding,
    Snippet,
    Component,
)
from mastf.MASTF.utils.enum import ProtectionLevel, Severity, ComponentCategory

logger = logging.getLogger(__name__)


def get_manifest_info(scanner: AbstractScanner) -> None:
    # Collect detailed information about permissions, components and
    # intent filters
    content_dir = scanner.file_dir / "contents"
    manifest_files = content_dir.glob("*/**/AndroidManifest.xml")

    scanner.observer.update("Running manifest analysis...", do_log=True)
    for manifest in manifest_files:
        run_manifest_scan(
            scanner,
            manifest,
        )


def run_manifest_scan(scanner: AbstractScanner, manifest_file: pathlib.Path):
    visitor = AXmlVisitor()
    handler = AndroidManifestHandler(scanner, manifest_file)

    if manifest_file.exists():
        try:
            with open(str(manifest_file), "rb") as mfp:
                document = parse(mfp)

        except Exception as err:
            scanner.observer.update(
                "[%s] Skipping manifest due to parsing error: %s",
                type(err).__name__,
                str(err),
                do_log=True,
                log_level=logging.ERROR,
            )
            return

        handler.link(visitor)
        visitor.visit_document(document)
    else:
        scanner.observer.update(
            "Skipped %s due to non-existed file!", str(manifest_file), do_log=True
        )


class AndroidManifestHandler:
    def __init__(
        self, scanner: AbstractScanner, path: pathlib.Path, observer: Observer = None
    ) -> None:
        self.scanner = scanner
        self.path = path
        self.observer = observer
        self.snippet = Snippet(language="xml", file_name=path.name)
        self._saved = False

    @property
    def scan(self) -> Scan:
        return self.task.scan

    def link(self, visitor: AXmlVisitor) -> None:
        # TODO: link visitor to instance methods
        visitor.uses_permission.add("android:name", self.on_permission)

        for name in list(ComponentCategory):
            name = str(name).lower()
            if hasattr(visitor, name):
                getattr(visitor, name).add("android:name", getattr(self, f"on_{name}"))

    def on_permission(self, element: Element, identifier: str) -> None:
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

        PermissionFinding.objects.create(
            pk=str(uuid.uuid4()),
            scan=self.scan,
            snippet=self.snippet,
            severity=Severity.MEDIUM if permission.dangerous else Severity.NONE,
            scanner=self.task.scanner,
            permission=permission,
        )

    def on_application(self, element: Element, name: str) -> None:
        self.handle_component(element, "application", name)

    def on_service(self, element: Element, name: str) -> None:
        self.handle_component(element, "service", name)

    def on_provider(self, element: Element, name: str) -> None:
        self.handle_component(element, "provider", name)

    def on_receiver(self, element: Element, name: str) -> None:
        self.handle_component(element, "receiver", name)

    def on_activity(self, element: Element, name: str) -> None:
        self.handle_component(element, "activity", name)

    def handle_component(self, element: Element, ctype: str, name: str) -> None:
        component = Component.objects.create(
            cid=Component.make_uuid(),
            scanner=self.scanner.scan_task.scanner,
            name=name,
            category=ctype.capitalize(),
            is_exported=element.getAttribute("android:name") == "true",
        )

        # TODO: if exported add Finding
        for intent_filter in element.childNodes:
            if intent_filter.nodeName == "intent-filter":
                action = intent_filter.getAttribute("android:name")
                component.intent_filters.add(
                    IntentFilter.objects.create(
                        name=action.split(".")[-2], action=action
                    )
                )

                if action == "android.intent.action.MAIN":
                    component.is_main = True
                elif action == "android.intent.category.LAUNCHER":
                    component.is_launcher = True


        # TODO: add findings
        component.save()
