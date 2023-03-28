import os
import hashlib

from django.http import HttpRequest
from django.shortcuts import render
from django.core.files.uploadedfile import UploadedFile

def render_error(request: HttpRequest, error: dict):
    return render(request, "error.html", context={'error': error})

def handle_file_upload(content: UploadedFile, extension: str) -> str:
    '''Writes an uploaded file to the /tmp directory.'''

    name = hashlib.md5(content.name.encode('utf-8')).hexdigest()
    file_path = os.path.join('/tmp', '%s.%s' % (name, extension))

    # Small fix if multiple files are uploaded and/or  handled
    # at the same time (not more than 10)
    for i in range(1, 10):
        if os.path.exists(file_path):
            file_path = '/tmp/%s-%d.%s' % (name, i, extension)
        else: break
    
    if os.path.exists(file_path):
        return None
    
    with open(file_path, 'wb+') as fp:    
        for chunk in content.chunks(8192):
            fp.write(chunk)
    
    return file_path
