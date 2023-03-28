import shutil

from uuid import uuid4

from django.http.request import HttpRequest
from django.http import JsonResponse

from mastf.MASTF import settings
from mastf.MASTF.forms import ProjectForm, ProjectDeleteForm
from mastf.MASTF.views.api.api_middleware import api_response, api_error
from mastf.MASTF.models import Project, AccountData
from mastf.MASTF.utils.helpers import http_request, new_error
from mastf.MASTF.const import (
    ERRORS, INVALID_PROJECT_FORM
)


#################################################################
# API functions
#################################################################
@http_request(['POST'])
def api_new_project(request: HttpRequest) -> JsonResponse:
    form = ProjectForm(request.POST)
    if not form.is_valid():
        return api_error(ERRORS[INVALID_PROJECT_FORM])

    if not request.user.is_authenticated:
        return api_response({'success': False}, code=401)

    project_id = str(uuid4())
    project = Project(
        project_uuid=project_id, name=form.data["project_name"],
        visibility=form.data['visibility'], tags=str(form.data['tags']),
        owner=request.user
    )

    path = settings.PROJECTS_ROOT / project_id
    try:
        path.mkdir()
    except OSError:
        return api_error(new_error(code=507, title="Could not create project directory"))
    
    project.save()
    return api_response({"success": True})

@http_request(['POST'])
def api_delete_project(request: HttpRequest) -> JsonResponse:
    form = ProjectDeleteForm(request.POST)
    if not form.is_valid():
        return api_error(new_error(
            title="Invalid form data", description="The provided Form data is invalid"))

    if not request.user.is_authenticated:
        return api_response({'success': False}, code=401)

    project_uuid = form.data['project_uuid']
    result = Project.objects.filter(project_uuid=project_uuid)
    if not result.exists():
        return api_error(new_error(title="Project not found!"))
    
    project = result.first()
    if project.owner != request.user:
        if project.visibility.lower() == 'public':
            # TODO: ass internal group checks
            pass
        else:
            return api_error(new_error(title="Project not found!"))

    path = settings.PROJECTS_ROOT / project_uuid
    try:
        shutil.rmtree(path)
    except OSError:
        return api_error(new_error(code=500, title="Could not delete project directory"))

    result.first().delete()
    return api_response({"success": True})
