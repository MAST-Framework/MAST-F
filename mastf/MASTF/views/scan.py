import json

from django.shortcuts import render
from django.urls import reverse
from django.http.request import HttpRequest
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from mastf.MASTF import settings
from mastf.MASTF.utils.helpers import http_request, new_error
from mastf.MASTF.views.api.api_middleware import error_from
from mastf.MASTF.views.api.api_scans import (
    api_new_scan,
)

from mastf.MASTF.const import (
    TMP_ERROR, ERRORS, INVALID_PROJECT_FORM
)
from mastf.MASTF.models import Project

from mastf.MASTF.scanners.plugin import ScannerPlugin


@http_request(['POST'])
@login_required(login_url="/login")
def new_scan(request: HttpRequest):
    response = api_new_scan(request)
    
    if response.status_code == 200:
        return HttpResponseRedirect(reverse("Projects"))
    else:
        return render(request, TMP_ERROR, context={
            'error': error_from(response), 
            'prev_url': request.headers.get('referer', '/')
        })

                      
@http_request(['GET'])
@login_required(login_url="/login")
def scan_results(request: HttpRequest, project_id, name: str, extension=None):
    plugin: ScannerPlugin = ScannerPlugin.all().get(name, None)
    if not plugin:
        return render(request, TMP_ERROR, context={
            'error': new_error(title='Plugin not found'),
            'prev_url': request.headers.get('referrer', '/')
        })
    
    extensions = plugin.extensions
    if len(extensions) == 0:
        return render(request, TMP_ERROR, context={
            'error': new_error(title='Invalid Scanner', 
                description='This scanner does not support any extensions'),
            'prev_url': request.headers.get('referrer', '/')
        })
        
    if not extension:
        extension = extensions[0]
    else:
        if extension not in extensions:
            return render(request, TMP_ERROR, context={
                'error': new_error(code=404, title='Extension not found'),
                'prev_url': request.headers.get('referrer', '/')
            })
    
    project = Project.objects.filter(project_uuid=project_id).first()
    if not project:
        return render(request, TMP_ERROR, context={
                'error': new_error(code=404, title='Project not found'),
                'prev_url': request.headers.get('referrer', '/')
            })
    
    context = plugin.context(extension, project)
    context.update({
        'extensions': extensions,
        'scanner_name': name,
        'project': Project.objects.get(project_uuid=project_id),
        'active': f"tabs-{extension}"
    })
    return render(request, "project/project-scan-results.html", context)
    
def scan_results_details(request: HttpRequest, project_id, name: str):
    return render(request, "project/project-scan-results.html", context={
        'extensions': {
            'details': {
                'url': 'ScanResultDetails'
            },
            'vulnerabilities': {
                'url': "ScanResultVulnerabilities",
            },
            'permissions': {
                'url': "ScanResultPermissions",
            },
        },
        'scanner_name': name,
        'active': 'tabs-details',
        'project': Project.objects.filter(project_uuid=project_id).first(),
        
        'data': {
            'cvss': "6.6",
            "risk_level": "Medium",
            "tracker_count": 4,
            'file': {
                'name': "Sample.apk",
                'size': "20MB",
                'md5': "0953143abc65h374021"
            },
            'store': {
                'name': 'Playstore',
                'fields': [
                    {
                        'value': 'Sample App',
                        'name': 'Title',
                        'type': 'str'
                    },
                    {
                        'name': 'Link',
                        'link': '#',
                        'value': 'Sample Link',
                        'type': 'link'
                    },
                    {
                        'name': 'Badge',
                        'type': 'badge',
                        'color': 'bg-red-lt',
                        'value': 'Sample Badge'
                    }
                ]
            }
        }
    })
 