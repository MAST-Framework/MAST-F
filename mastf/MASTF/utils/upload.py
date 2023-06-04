# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
__doc__ = """
Simple and small module that covers file uploads and checksum calculation
as well as string extraction of a file.
"""
import os
import hashlib
import logging

from io import IOBase

from django.core.files.uploadedfile import TemporaryUploadedFile

from mastf.MASTF import settings
from mastf.MASTF.models import Project, File

logger = logging.getLogger(__name__)


def checksum_from_path(file_path: str) -> tuple:
    """Calculates SHA256, SHA1 and MD5 for the file at the given path.

    :param file_path: the absolute file path
    :type file_path: str
    :return: sha256, sha1 and md5 of the given file
    :rtype: tuple
    """
    if not os.path.exists(file_path):
        return None, None, None

    with open(file_path, "rb", buffering=0) as fp:
        return get_file_checksum(fp)


# TODO: strings


def get_file_checksum(fp: IOBase) -> tuple:
    """Efficient way to cumpute sha256, sha1 and md5 checksum

    :param fp: the file pointer object
    :type fp: IOBase
    :return: sha256, sha1 and md5 of the given file
    :rtype: tuple
    """
    fp.seek(0)
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()

    buf = bytearray(128 * 1024)
    view = memoryview(buf)
    for chunk in iter(lambda: fp.readinto(view), 0):
        sha256.update(view[:chunk])
        sha1.update(view[:chunk])
        md5.update(view[:chunk])

    return sha256.hexdigest(), sha1.hexdigest(), md5.hexdigest()


def handle_scan_file_upload(
    file: TemporaryUploadedFile, project: Project
):
    """Handles a generic file upload to the given project.

    :param file: the file to be saved
    :type file: TemporaryUploadedFile
    :param project: the target project
    :type project: Project
    :return: a :class:`File` object on success, ``None`` otherwise
    :rtype: :class:`File` | ``NoneType``
    """
    internal_name = hashlib.md5(file.name.encode()).hexdigest()

    suffix = f".{file.name.split('.')[-1]}" if "." in file.name else ""
    path = (
        settings.PROJECTS_ROOT / str(project.project_uuid)
    ) / f"{internal_name}{suffix}"
    if path.exists():
        logger.info("Uploaded file destination already exists! (%s)", str(path))
        return File.objects.get(file_path=str(path))

    return handle_file_upload(file, internal_name, str(path), save=True)

def handle_file_upload(
    file: TemporaryUploadedFile, internal_name: str, path: str, save: bool = True
) -> File:
    # TODO: maybe add input validation
    with open(path, "wb") as dest:
        if file.multiple_chunks():
            for chunk in file.chunks(8192):
                if chunk:
                    dest.write(chunk)
        else:
            dest.write(file.read())

    sha256, sha1, md5 = checksum_from_path(path)
    if not sha256 and not sha1 and not md5:
        logger.warning("Could not calculate checksums for uploaded file")
        return None

    db_file = File(
        md5=md5,
        sha1=sha1,
        sha256=sha256,
        file_name=file.name,
        file_size=file.size,
        file_path=str(path),
        internal_name=internal_name,
    )
    if save:
        db_file.save()
    return db_file
