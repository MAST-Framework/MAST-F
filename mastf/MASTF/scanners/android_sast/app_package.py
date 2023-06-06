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
from __future__ import annotations

import logging
import lief
import uuid
import pathlib

from androguard.core.bytecodes import apk

from LibScout.config import FILE_EXT_LIB_PROFILE
from LibScout.pkg import to_packages, to_path, get_framework_pt
from LibScout.profile.caches import LazyPickleCache
from LibScout.core.matcher import LibMatcher

from mastf.core.files.properties import Properties
from mastf.core.files.tpl import TPL

from mastf.MASTF.models import Package, Dependency
from mastf.MASTF.scanners.plugin import ScannerPluginTask

logger = logging.getLogger(__name__)


def get_app_packages(task: ScannerPluginTask) -> None:
    # TODO: Use python package mastf-libscout to scan the given
    # apk file for possible dependencies. The output returns a possible
    # description, so we can add it if no template was found
    apk_file: apk.APK = task[apk.APK]
    base_dir = task.file_dir / "contents"
    dependencies: dict[Package, Dependency] = {}

    # ======================= Heuristic Approach =======================
    # Rather use lief.DEX.parse as we just want all class names. The used
    # dictionary stores the package, possible version number, type and
    # license (if found)
    for dex_content in apk_file.get_all_dex():
        dex_file = lief.DEX.parse(dex_content)
        for class_def in dex_file.classes:
            # filter out any non-existend files
            if not class_def.source_filename:
                continue

            name = to_path(*to_packages(class_def.pretty_name))
            queryset = Package.objects.filter(group_id=name)
            # If we have an exact match, we should add it to the matched
            # packages as we don't know the artifact id
            if queryset.exists() and len(queryset) == 1:
                package = queryset.first()
                if package not in dependencies:
                    dependencies[package] = Dependency(pk=uuid.uuid4(), package=package)

    # Before we are going to add the packages, we try to look at other
    # places to collect version numbers:
    # 1: general ".properties" files
    for config in base_dir.rglob("*.properties"):
        properties = Properties(str(config))
        query = {}
        version = properties.get("version")
        # Only add property files with client and version as possible dependencies
        if "client" in properties:
            query["artifact_id"] = properties["client"]

        elif "groupId" in properties:
            # These special properies files are placed by maven and may contain
            # the full group+artifact ID
            query["group_id"] = properties["groupId"]
            if "artifactId" in properties:
                query["artifact_id"] = properties["artifactId"]

        queryset = Package.objects.filter(**query)
        if queryset.exists() and len(queryset) == 1:
            package = queryset.first()
            # If the package is already present, check if there is a version mapped to it
            if package in dependencies:
                dep = dependencies[package]
                if not dep.version and version:
                    # Set the version if not already specified
                    dep.version = version
            else:
                dependencies[package] = Dependency(pk=uuid.uuid4(), package=package, version=version)

    # 2: .version files (mostly Android related frameworks)
    for config in base_dir.rglob("*.version"):
        group_id, artifact_id = config.stem.split("_", 1)

        # Limit the amount of read operations to existing packages
        queryset = Package.objects.filter(group_id=group_id, artifact_id=artifact_id)
        if queryset.exists() and len(queryset) == 1:
            package = queryset.first()
            # Read version
            with open(str(config), "r", encoding="utf-8") as fp:
                # These files only contain one line, so we can call .readline()
                version = fp.readline().strip()

            if package not in dependencies:
                dependencies[package] = Dependency(pk=uuid.uuid4(), package=package, version=version)
            else:
                dep = dependencies[package]
                if version and not dep.version:
                    dep.version = version

    # 3: TPL metadata files (huge files with license metadata - may contain
    # group and artifact ids)
    for tpl_meta in base_dir.rglob("third_party_license_metadata"):
        # There will be only one file (if existend)
        with TPL(str(tpl_meta)) as tpl_iterator:
            # TODO: Here we have to implement a mechanism that parses
            # the ids and License name at the same time.
            for group_id, artifact_id in tpl_iterator:
                query = {}
                if group_id:
                    query["group_id"] = group_id
                if artifact_id:
                    query["artifact_id"] = artifact_id

                queryset = Package.objects.filter(**query)
                # These checks are pointless as there will be only one or no match
                if queryset.exists() and len(queryset) == 1:
                    package = queryset.first()
                    # If the package is already present, check if there is a version mapped to it
                    if package not in dependencies:
                        dependencies[package] = Dependency(pk=uuid.uuid4(), package=package)

    # 4: Cordova dependencies (TODO)
    # ...

    # Add all dependencies to the current scan if not already present
    present_packages = set(map(lambda x: x.package, Dependency.objects.filter(project=task.scan.project)))
    for package in dependencies:
        dependency = dependencies[package]
        if package in present_packages:
            continue # just ignore duplicates

        dependency.project = task.scan.project
        dependency.scanner = task.scan_task.scanner
        # TODO: dependency.outdated = ...

    Dependency.objects.bulk_create(dependencies.values())

def run_libscout_scan(task: ScannerPluginTask, profiles_dir: str, android_jar: str) -> None:
    # config:
    #   - android.jar path
    #   - profiles directory

    # NOTE: We use a LazyPickleCache as importing a huge amount
    # of profiles into memory wouldn't be efficient if we have
    # multiple libscout scans at a time.
    cache = LazyPickleCache()
    tree = get_framework_pt(android_jar)

    # 1. Load compiled profile paths
    for file_path in pathlib.Path(profiles_dir).rglob(f"*.{FILE_EXT_LIB_PROFILE}"):
        cache.import_profile(str(file_path))

    # 2. Create matcher instance
    matcher = LibMatcher(cache=cache, fwpt=tree)

    # 3. run scan
    stats = matcher.identify_libs(task.scan.file.file_path)

    # TODO: artifact+groupid in package-only-matches
    # TODO: verify partial+full_matches