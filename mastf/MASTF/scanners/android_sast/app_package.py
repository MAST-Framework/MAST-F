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
import logging

from androguard.core.bytecodes import apk, dvm

from mastf.MASTF.models import Package, Dependency, Scanner
from mastf.MASTF.utils.enum import Platform
from mastf.MASTF.scanners.plugin import ScannerPluginTask

logger = logging.getLogger(__name__)

def get_app_packages(task: ScannerPluginTask) -> None:
    apk_file: apk.APK = task[apk.APK]

    dex_files = list(map(dvm.DalvikVMFormat, apk_file.get_all_dex()))
    class_names = []
    for dvm_file in dex_files:
        class_names.extend(dvm_file.get_classes_names())

    for name in set(class_names):
        group_id = str(name).lower().replace("/", ".")[1:-1]
        queryset = Package.objects.filter(platform=Platform.ANDROID, group_id=group_id)
        if len(queryset) == 1:
            # only one package, so we can definitely add it
            add_package(queryset.first(), task.scan_task.scanner)
        else:
            # Dumping package id
            logger.info(group_id)

    # TODO: native dependencies


def add_package(package: Package, scanner: Scanner, version: str = None) -> None:
    # TODO: add scraper the check for higher version number
    pass




