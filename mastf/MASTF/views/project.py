from django.shortcuts import render
from django.urls import reverse
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from mastf.MASTF.utils.helpers import http_request, new_error
from mastf.MASTF.utils.shortcuts import render_error
from mastf.MASTF.views.api.api_projects import (
    api_new_project, api_delete_project
)

from mastf.MASTF.const import (
    TMP_OVERVIEW, ERRORS, UNKNOWN_PROJECT_ID, INVALID_PROJECT_FORM
)
from mastf.MASTF.views.api.api_context import (
    api_get_project_scan_history_context,
    api_get_project_overview_context,
    api_get_project_scan_data_context
)

@login_required(login_url="/login")
def overview(request: HttpRequest, project_id):
    context = api_get_project_overview_context(request.user, project_id)
    if not context['project']:
        return render_error(request, ERRORS[UNKNOWN_PROJECT_ID])
    
    return render(request, TMP_OVERVIEW, context)

@login_required(login_url="/login")
def scan_history(request: HttpRequest, project_id):
    context = api_get_project_scan_history_context(request.user, project_id)
    if not context['project']:
        return render_error(request, ERRORS[UNKNOWN_PROJECT_ID])
    
    return render(request, TMP_OVERVIEW, context)

@login_required(login_url="/login")
def scanners_results(request: HttpRequest, project_id: str):
    context = api_get_project_scan_data_context(request.user, project_id)
    if not context['project']:
        return render_error(request, ERRORS[UNKNOWN_PROJECT_ID])
    
    return render(request, TMP_OVERVIEW, context)

@http_request(['POST'])
@login_required(login_url="/login")
def new_project(request: HttpRequest):
    response = api_new_project(request)

    if response.status_code == 200:
        return HttpResponseRedirect(reverse("Projects"))
    else:
        return render(request, "error.html", context={'error': ERRORS[INVALID_PROJECT_FORM]})

@http_request(['POST'])
@login_required(login_url="/login")
def delete_project(request: HttpRequest):
    response = api_delete_project(request)
    
    if response.status_code == 200:
        return HttpResponseRedirect(reverse("Projects"))
    else:
        return render(request, "error.html", context={'error': ERRORS[UNKNOWN_PROJECT_ID]})

                      
