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

from androguard.core.bytecodes import apk

from mastf.MASTF.models import Package, Scanner
from mastf.MASTF.scanners.plugin import ScannerPluginTask

logger = logging.getLogger(__name__)

def get_app_packages(task: ScannerPluginTask) -> None:
    # TODO: Use python package mastf-libscout to scan the given
    # apk file for possible dependencies. The output returns a possible
    # description, so we can add it if no template was found
    apk_file: apk.APK = task[apk.APK]

    # Rather use lief.DEX.parse as we just want all class names

def add_package(package: Package, scanner: Scanner, version: str = None) -> None:
    # TODO: add scraper the check for higher version number
    pass




