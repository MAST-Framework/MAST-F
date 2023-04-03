from django.http import Http404

from mastf.MASTF.mixins import ContextMixinBase, UserProjectMixin
from mastf.MASTF.scanners.plugin import ScannerPlugin

__all__ = [
    'ScannerResultsView'
]

class ScannerResultsView(UserProjectMixin, ContextMixinBase):
    template_name = 'project/project-scan-results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.apply_project_context(context, self.kwargs['project_uuid'])

        plugins = ScannerPlugin.all_of(context['project'])
        name = self.kwargs['name']
        extension = self.kwargs['extension']
        if name not in plugins:
            raise Http404

        plugin: ScannerPlugin = plugins[name]
        if extension not in plugin.extensions:
            raise Http404

        context["extensions"] = plugin.extensions
        context['scanner_name'] = name
        context['active'] = f"tabs-{extension}"
        context['data'] = plugin.context(extension, context['project'])
        return context

