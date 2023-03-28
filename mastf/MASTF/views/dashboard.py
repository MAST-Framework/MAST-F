from django.shortcuts import render
from django.urls import reverse
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from mastf.MASTF.views.api.api_context import (
    api_get_application_context,
    api_get_project_context,
    api_get_context
)
from mastf.MASTF.models import Project, AccountData

@login_required(login_url="/login")
def index(request: HttpRequest):
    return render(request, "index.html", api_get_context(request.user, {
        'selected': 'Home'
    }))

@login_required(login_url="/login")
def applications_and_projects(request: HttpRequest):
    if (request.path.endswith('projects')
            or request.path.rstrip('/').endswith('applicationsAndProjects')):
        context = api_get_project_context(request.user)
        users = (list(Project.objects.filter(owner=request.user))
            + list(Project.objects.filter(visibility='public').exclude(owner=request.user))
        )
        for project in users:
            context['project_table_data'].append({
                "ID": project.project_uuid,
                "Project Name": project.name,
                "Last Scan Origin": "-",
                "Last Scan": "-",
                "Tags": [] if not project.tags else project.tags.split(','),
                "Groups": [

                ],
                "Risk Level": {
                    "text": "None",
                    "bg_color": "bg-secondary-lt"
                },
                "High": 0,
                "Medium": 0,
                "Low": 0,
            })

    else:
        context = api_get_application_context(request.user)

    return render(request, "dashboard/applications-and-projects.html", context)

@login_required(login_url="/login")
def user_settings(request: HttpRequest):
    return render(request, "user/settings.html", 
        api_get_context(request.user, {
            
        }))