# MAST-F
 Mobile Application Security Testing Framework (MAST-F) for iOS and Android.

[![python](https://img.shields.io/badge/python-3.8+-blue.svg?logo=python&labelColor=lightgrey)](https://www.python.org/downloads/)

## MASTF Structure

```bash
MASTF/ # django-app
    rest/ # directory with all API endpoints
    web/ # directory with all web frontend endpoints
    scanners/ # module for placing scanners
    models.py # global database models
    converters.py # URL converters for django
    forms.py # django forms
    serializers.py # serializer classes for the REST-API
    settings.py # server settings
    urls.py # global URL definitions
```

## Projects Directory Structure

The directory structure of a simple project can be summarized to the following:

```bash
projects/
    <uuid:project_uuid>/
        uploadedFile.[apk|ipa]
        src/
            [ java/ ]
            [ smali/ ]
            [ swift/ ]
            [ assembler/ ]
        contents/
            # initial ZIP-File data
```
    