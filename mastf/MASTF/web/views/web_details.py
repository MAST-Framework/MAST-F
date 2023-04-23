import json

from django.shortcuts import redirect
from django.contrib import messages

from mastf.MASTF.settings import DETAILS_DIR, ARTICLES
from mastf.MASTF.mixins import ContextMixinBase, TemplateAPIView


class DetailsView(ContextMixinBase, TemplateAPIView):
    template_name = "details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        platform = self.kwargs['platform'].lower()
        name = self.kwargs['name'].lower()

        path = DETAILS_DIR / platform / f"{name}.jsontx"
        if not path.exists():
            messages.warning(self.request, f'Invalid details name: {path}', "FileNotFoundError")
            return context

        with open(str(path), "r", encoding="utf-8") as fp:
            context["data"] = json.load(fp)

        context['pages'] = ARTICLES
        return context
