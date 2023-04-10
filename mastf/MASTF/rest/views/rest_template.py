from uuid import uuid4

from rest_framework import permissions, authentication

from mastf.MASTF.serializers import TemplateSerializer
from mastf.MASTF.models import FindingTemplate
from mastf.MASTF.forms import FindingTemplateForm

from .base import APIViewBase, CreationAPIViewBase, ListAPIViewBase

__all__ = [
    'FindingTemplateView', 'FindingTemplateListView',
    'FindingTemplateCreationView'
]

class FindingTemplateView(APIViewBase):
    """API-Endpoint for creating, managing and removing finding templates."""

    permission_classes = [permissions.IsAuthenticated]

    model = FindingTemplate
    lookup_field = 'template_id'
    serializer_class = TemplateSerializer
    

class FindingTemplateCreationView(CreationAPIViewBase):
    """Separate APIView for creating new ``FindingTemplate`` objects"""

    permission_classes = [permissions.IsAuthenticated]
    form_class = FindingTemplateForm
    model = FindingTemplate
    
    def make_uuid(self):
        return f"FT-{uuid4()}-{uuid4()}"


class FindingTemplateListView(ListAPIViewBase):
    """A view listing all finding templates"""

    queryset = FindingTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TemplateSerializer
