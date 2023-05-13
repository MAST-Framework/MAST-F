import pathlib
import logging
import uuid

from xml.dom.minidom import Element, parse

from mastf.android.manifest import AXmlVisitor
from mastf.MASTF.models import (
    Scan,
    ScanTask,
    AppPermission,
    PermissionFinding,
    Snippet,
    Component
)
from mastf.MASTF.utils.enum import ProtectionLevel, Severity

logger = logging.getLogger(__name__)


def run_manifest_scan(task: ScanTask, manifest_file: pathlib.Path):
    visitor = AXmlVisitor()
    handler = AndroidManifestHandler(task, manifest_file)

    if manifest_file.exists():
        try:
            with open(str(manifest_file), "rb") as mfp:
                document = parse(mfp)

        except Exception as err:
            logger.debug(
                "[%s] Skipping manifest due to parsing error: %s",
                type(err).__name__,
                str(err),
            )
            return

        handler.link(visitor)
        visitor.visit_document(document)
    else:
        logger.debug("Skipped %s due to non-existed file!", str(manifest_file))


class AndroidManifestHandler:
    def __init__(self, task: ScanTask, path: pathlib.Path) -> None:
        self.task = task
        self.path = path
        self.snippet = Snippet(language="xml", file_name=path.name)
        self._saved = False

    @property
    def scan(self) -> Scan:
        return self.task.scan

    def link(self, visitor: AXmlVisitor) -> None:
        # TODO: link visitor to instance methods
        visitor.uses_permission.add("android:name", self.on_permission)
        visitor.application.add("android:name", self.on_application)

    def on_permission(self, element: Element, identifier: str) -> None:
        queryset = AppPermission.objects.filter(identifier=identifier)

        protection_level = str(
            element.getAttribute("android:protectionLevel") or ""
        ).capitalize()
        if not protection_level:
            protection_level = ProtectionLevel.NORMAL
        else:
            if protection_level not in list(ProtectionLevel):
                logger.debug(
                    "Switching unknown ProtectionLevel classifier: %s", protection_level
                )
                protection_level = ProtectionLevel.NORMAL

        if not queryset.exists():
            logger.debug(
                "Creating new Permission: %s [pLevel=%s]", identifier, protection_level
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
            severity=Severity.MEDIUM if permission.is_dangerous else Severity.NONE,
            scanner=self.task.scanner,
            permission=permission,
        )

    def on_application(self, element: Element, name: str) -> None:
        exported = element.getAttribute("android:exported")

        Component.objects.create(
            pk=Component.make_uuid(), is_exported=...
        )