# TODO:deprecated
import os
import hashlib
import logging

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import TemporaryUploadedFile

from mastf.MASTF import settings
from mastf.MASTF.models import Project, File

logger = logging.getLogger(__name__)
storage = FileSystemStorage()

def checksum_from_path(file_path: str) -> tuple:
    if not os.path.exists(file_path):
        return None, None, None

    with open(file_path, 'rb', buffering=0) as fp:
        return get_file_cheksum(fp)


def get_file_cheksum(fp) -> tuple:
    """Efficient way to cumpute sha256, sha1 and md5 checksum"""
    fp.seek(0)
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()

    buf = bytearray(128*1024)
    view = memoryview(buf)
    for chunk in iter(lambda: fp.readinto(view), 0):
        sha256.update(view[:chunk])
        sha1.update(view[:chunk])
        md5.update(view[:chunk])

    return sha256.hexdigest(), sha1.hexdigest(), md5.hexdigest()

def handle_scan_file_upload(file: TemporaryUploadedFile, project: Project):
    internal_name = hashlib.md5(file.name.encode()).hexdigest()

    suffix = f".{file.name.split('.')[-1]}" if '.' in file.name else ""
    path = (settings.PROJECTS_ROOT / str(project.project_uuid)) / f"{internal_name}{suffix}"
    if path.exists():
        logger.info('Uploaded file destination already exists!')
        return File.objects.get(file_path=str(path))

    with open(path, 'wb') as dest:
        if file.multiple_chunks():
            for chunk in file.chunks(8192):
                if chunk:
                    dest.write(chunk)
        else:
            dest.write(file.read())

    sha256, sha1, md5 = checksum_from_path(path)
    if not sha256 and not sha1 and not md5:
        logger.warning('Could not calculate checksums for uploaded file')
        return None

    db_file = File(md5=md5, sha1=sha1, sha256=sha256,
                   file_name=file.name, file_size=file.size,
                   file_path=str(path), internal_name=internal_name)
    db_file.save()
    return db_file