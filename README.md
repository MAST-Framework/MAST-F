# MAST-F
 Mobile Application Security Testing Framework (MAST-F) for iOS and Android.

[![python](https://img.shields.io/badge/python-3.8+-blue.svg?logo=python&labelColor=lightgrey)](https://www.python.org/downloads/)

## MASTF Structure

```bash
MASTF/ # django-app
    rest/ # directory with all API endpoints
    web/ # directory with all web frontend endpoints
    scanners/ # module for placing scanners
    models/ # global database models
    converters.py # URL converters for django
    forms/ # django forms
    serializers/ # serializer classes for the REST-API
    settings.py # server settings
    urls.py # global URL definitions
```

## Projects Directory Structure

The directory structure of a simple project can be summarized to the following:

```bash
projects/
    <uuid:project_uuid>/
        uploadedFile.[apk|ipa]
        <md5:file_md5>/
            src/
                [ java/ ]
                [ smali/ ]
                [ swift/ ]
                [ assembler/ ]
            contents/
                # initial ZIP-File data
```


## ScanTask design

After a new scan has been requested, it will be executed on the target scan date. Before each
scanner is exeuted, there is a preparation task, that is called asynchronously:

    1. Preparation: create directories, extract ZIP Files, decompile binaries
    2. Call Plugins: each scanner comes with a ``task`` field that should be 
        a function that takes a ``Scan`` and ``ScanTask`` object as input.
    
