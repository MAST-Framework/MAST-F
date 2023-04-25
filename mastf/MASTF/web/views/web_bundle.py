from django.shortcuts import redirect
from django.db.models import QuerySet, Q

from mastf.MASTF.mixins import (
    ContextMixinBase,
    UserProjectMixin,
    VulnContextMixin,
    TemplateAPIView
)
from mastf.MASTF.models import (
    Bundle, Project
)
from mastf.MASTF.rest.permissions import IsBundleMember

__all__ = [
    'BundleDetailsView'
]

class BundleDetailsView(ContextMixinBase, TemplateAPIView):
    template_name = "bundle/bundle-overview.html"
    permission_classes = [IsBundleMember]

    def get_context_data(self, **kwargs: dict) -> dict:
        context = super().get_context_data(**kwargs)

        context['bundle'] = self.get_object(Bundle, pk_field='bundle_id')
        context['active'] = 'tabs-overview'
        return context