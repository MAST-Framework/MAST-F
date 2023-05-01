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
scanner is executed, there is a preparation task, that is called asynchronously:

    1. Preparation: create directories, extract ZIP Files, decompile binaries
    2. Call Plugins: each scanner comes with a ``task`` field that should be
        a function that takes a ``Scan`` and ``ScanTask`` object as input.


## `base.html` Structure

1. `title`: typically contains the title of the page, which is displayed in the browser's title bar and used by search engines to determine the page's content.
2. `css_extended`: used to include any additional CSS styles beyond the basic styles included in the base template. This can include custom styles for the current page or any dependencies that are required.
3. `navbar`: The navbar section contains the navigation menu, which usually consists of links to other pages on the website. It is typically displayed at the top of the page and is used to help users navigate the site.
4. `page_before`: used for any content that needs to appear before the main content of the page. This can include things like a header image, a call-to-action banner, or any other content that should be displayed prominently.
5. `page_header`: contains the header of the main content section of the page. It is typically used to display the main title of the page, along with any other information that should appear at the top of the content section.
6. `page_body`: contains the main content of the page. This can include text, images, videos, or any other type of content that is relevant to the page.
7. `footer`: stores information that is common across all pages of the site, such as copyright information, contact details, and links to social media accounts.
8. `modals`: used to display any pop-up windows or different forms, that need to be displayed on the page.
9. `alerts`: used to display any notifications or alerts to the user. This can include messages about errors, success messages, or any other type of notification that the user needs to be aware of.
10. `js_extended`: used to include any additional JavaScript code beyond the basic scripts included in the base template. This can include custom scripts for the current page or any dependencies that are required.
