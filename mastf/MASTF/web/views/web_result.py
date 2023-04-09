from django.contrib import messages

from mastf.MASTF.mixins import ContextMixinBase, UserProjectMixin, TemplateAPIView
from mastf.MASTF.rest.permissions import IsOwnerOrPublic
from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF.models import File, Scan

__all__ = [
    'ScannerResultsView', 'ScanIndexView'
]

class ScanIndexView(UserProjectMixin, ContextMixinBase, TemplateAPIView):
    template_name = 'project/project-scan-results.html'
    permission_classes = [IsOwnerOrPublic]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.apply_project_context(context)

        project = context['project']
        # Apply scan files after permission check
        context['scan_files'] = Scan.files(project=project)
        return context

class ScannerResultsView(UserProjectMixin, ContextMixinBase, TemplateAPIView):
    template_name = 'project/project-scan-results.html'
    permission_classes = [IsOwnerOrPublic]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.apply_project_context(context)

        file_md5 = self.kwargs.get('file_md5', None)
        active_file = File.objects.filter(md5=file_md5).first()
        if not file_md5 or not active_file:
            messages.error(self.request, "Could not find file!", "FileNotFoundError")
            return context

        project = context['project']
        # Apply scan files after permission check
        context['scan_files'] = Scan.files(project=project)
        context['active_file'] = active_file
        context['scan'] = Scan.objects.filter(project=project, file=active_file)

        plugins = ScannerPlugin.all_of(project)
        name = self.kwargs['name']
        extension = self.kwargs.get('extension', None)
        if name not in plugins:
            messages.error(self.request, "Invalid scanner name for selected project", "404NotFoundError")
            return context

        plugin: ScannerPlugin = plugins[name]
        if extension not in plugin.extensions and extension is not None:
            messages.error(self.request, "Invalid extension name for selected scanner", "404NotFoundError")
            return context

        context["extensions"] = plugin.extensions
        context['scanner_name'] = name
        context['active'] = f"tabs-{extension}"
        context['data'] = plugin.context(extension, project, active_file)
        return context

