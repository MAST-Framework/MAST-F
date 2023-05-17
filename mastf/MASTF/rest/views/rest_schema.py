from rest_framework import authentication, permissions

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

__all__ = ["RestSchemaView"]

RestSchemaView = get_schema_view(
    openapi.Info(
        title="MAST-F REST API",
        default_version='v1',
        description="REST api documentation",
        license=openapi.License(name="GNU GPLv3"),
    ),
    authentication_classes=[
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
    ],
    permission_classes=[permissions.IsAuthenticated],
)
