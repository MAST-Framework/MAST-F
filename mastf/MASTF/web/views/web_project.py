
from mastf.MASTF.mixins import ContextMixinBase, UserProjectMixin

__all__ = [
    'UserProjectView'
]

class UserProjectView(UserProjectMixin, ContextMixinBase):
    template_name = 'project/project-overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.apply_project_context(context, self.kwargs['project_uuid'])
        return context
    
