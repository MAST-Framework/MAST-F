import logging
import pathlib
import tempfile
import os

from uuid import uuid4

from rest_framework import permissions
from rest_framework.views import APIView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request

from mastf.MASTF.serializers import AppPermissionSerializer
from mastf.MASTF.models import AppPermission
from mastf.MASTF.forms import AppPermissionForm
from mastf.MASTF.utils import upload

from mastf.core.files import apl

from .base import APIViewBase, ListAPIViewBase, CreationAPIViewBase

__all__ = [
    "AppPermissionView",
    "AppPermissionCreationView",
    "AppPermissionListView",
    "AppPermissionFileUpload",
]

logger = logging.getLogger(__name__)


class AppPermissionView(APIViewBase):
    """Basic API-Endpoint to update, delete and fetch app permissions"""

    permission_classes = [permissions.IsAuthenticated]
    model = AppPermission
    serializer_class = AppPermissionSerializer
    lookup_field = "permission_uuid"


class AppPermissionCreationView(CreationAPIViewBase):
    permission_classes = [permissions.IsAuthenticated]
    model = AppPermission
    form_class = AppPermissionForm


class AppPermissionListView(ListAPIViewBase):
    queryset = AppPermission.objects.all()
    serializer_class = AppPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class AppPermissionFileUpload(APIView):
    model = AppPermission

    def post(self, request: Request) -> Response:
        # Saving the file temporarily in the tmp-directory with a
        # random uuid4 as its name
        target_dir = pathlib.Path(tempfile.gettempdir())
        target_file = target_dir / str(uuid4())

        tmp_file = (request.FILES or {}).get("file")
        if not tmp_file:
            return Response(
                {"success": False, "detail": "Invalid Form data"},
                status.HTTP_400_BAD_REQUEST,
            )

        fileobj = upload.handle_file_upload(tmp_file, "", str(target_file), save=False)

        try:
            with open(str(target_file), "r") as fp:
                aplist = apl.load(fp)

            os.remove(str(target_file))
        except Exception as err:
            logger.exception(str(err))
            return Response({"success": False}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(
            "Importing APL from %s with checksum: %s", str(target_file), fileobj.sha256
        )
        pobjects = []
        for permission in aplist.permissions:
            pobjects.append(
                AppPermission(
                    permission_uuid=uuid4(),
                    identifier=permission.identifier,
                    name=permission.label or "<empty permission name>",
                    protection_level=AppPermission.PROTECTION_LEVEL_SEPARATOR.join(
                        permission.protectionLevel
                    ).lower(),
                    dangerous="dangerous" in permission.protectionLevel,
                    group="",  # ungrouped permissions don't have a group,
                    short_description=(
                        permission.description
                        or "Dynamic generated description. Please edit the short and long description in the plugins-context of your MAST-F Instance.",
                    ),
                )
            )

        for group in aplist.groups:
            group_permissions = group.permissions
            for permission in group_permissions:
                pobjects.append(
                    AppPermission(
                        permission_uuid=uuid4(),
                        identifier=permission.identifier,
                        name=permission.label or "<empty permission name>",
                        protection_level=AppPermission.PROTECTION_LEVEL_SEPARATOR.join(
                            permission.protectionLevel
                        ).lower(),
                        dangerous="dangerous" in permission.protectionLevel,
                        group=group.identifier,
                        short_description=(
                            permission.description
                            or "Dynamic generated description. Please edit the short and long description in the plugins-context of your MAST-F Instance.",
                        ),
                    )
                )

        logger.info("Creating %d permission objects", len(pobjects))
        AppPermission.objects.bulk_create(pobjects, update_conflicts=["identifier"])
        return Response({"success": True})
