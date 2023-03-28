from django.http import JsonResponse
from django.http.request import HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import TemporaryUploadedFile

from mastf.MASTF.scanners.plugin import ScannerPlugin
from mastf.MASTF import settings
from mastf.MASTF.models import Project, File, ProjectScanner
from mastf.MASTF.forms import ProjectScanForm
from mastf.MASTF.utils.checksum import checksum_from_path
from mastf.MASTF.utils.helpers import http_request, new_error
from mastf.MASTF.views.api.api_middleware import api_error, api_response

def handle_scan_file_upload(file: TemporaryUploadedFile, project_id: str) -> File:
    path = settings.PROJECTS_ROOT / str(project_id) / file.name

    if path.exists():
        return api_error(new_error(code=507, title="File already exists"))

    if not path.parent.exists():
        return api_error(new_error(code=507, title="Malformed project directory"))

    with open(path, 'wb') as dest:
        for chunk in file.chunks(8192):
            if chunk:
                dest.write(chunk)

    sha256, sha1, md5 = checksum_from_path(path)
    if not sha256 and not sha1 and not md5:
        return api_error(new_error(title="Could not calculate checksum for file"))

    db_file = File(md5=md5, sha1=sha1, sha256=sha256,
                   file_name=file.name, file_size=file.size)
    db_file.save()
    return db_file


@http_request(['POST'])
@login_required(login_url='/login')
def api_new_scan(request: HttpRequest):
    form = ProjectScanForm(request.POST, request.FILES)
    if not form.is_valid():
        return api_error(new_error(title="Invalid Form-Data"))

    project = Project.objects.filter(project_uuid=form.cleaned_data['project_id']).first()
    if not project or (project.owner != request.user
        and project.visibility.lower() != 'public'):
        return api_error(new_error(title="Unauthorized",
            description="The current user does not own the provided project"))


    scanners = ScannerPlugin.all()
    selected = []
    max_count = len(scanners)
    for i in range(max_count):
        name = request.POST.get(f"selected_scanners_{i}", None)
        if not name or name not in scanners:
            break
        
        if not ProjectScanner.objects.filter(project=project, scanner=name).exists():
            ProjectScanner(project=project, scanner=name).save()
        selected.append(name)

    if len(selected) == 0:
        return api_error(new_error(title="Invalid scanner count",
            description="A scan must contain at least one scanner!"))

    if not form.data.get('file_url', None):
        result = handle_scan_file_upload(request.FILES['file'], form.cleaned_data['project_id'])
        if isinstance(result, JsonResponse):
            return result
    else:
        ...

    # register scan tasks after preparation

