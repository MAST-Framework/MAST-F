"""MASTF URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path, register_converter

from mastf.MASTF import settings, converters

register_converter(converters.FindingTemplateIDConverter, 'ftid')
register_converter(converters.VulnerabilityIDConverter, 'svid')
register_converter(converters.FindingIDConverter, 'sfid')
register_converter(converters.MD5Converter, 'md5')

urlpatterns = [
    path('api/v1/', include('mastf.MASTF.rest.urls')),
]

if settings.DEBUG:
    urlpatterns.extend([
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ])

if not settings.API_ONLY:
    urlpatterns.extend([
        path("web/", include('mastf.MASTF.web.urls'))
    ])
