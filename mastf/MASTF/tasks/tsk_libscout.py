# This file is part of MAST-F's Backend API
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

import pathlib
import json
import uuid

from celery import shared_task
from celery.utils.log import get_task_logger

from LibScout.config import FILE_EXT_LIB_PROFILE
from LibScout.pkg import get_framework_pt
from LibScout.profile import export_app_stats
from LibScout.profile.caches import LazyPickleCache
from LibScout.core.matcher import LibMatcher

from mastf.core.progress import Observer

from mastf.MASTF.models import ScanTask, Package, Dependency

logger = get_task_logger(__name__)

__all__ = [ "perform_libscout_scan" ]

@shared_task(bind=True)
def perform_libscout_scan(
    self, scan_task_id: str, profiles_dir: str, android_jar: str
) -> dict:
    # config:
    #   - android.jar path
    #   - profiles directory
    scan_task = ScanTask.objects.get(task_uuid=scan_task_id)
    scan_task.celery_id = self.request.id
    scan_task.save()
    scan = scan_task.scan
    observer = Observer(self, scan_task=scan_task)

    observer.update("Setting up LibScout...")
    if not pathlib.Path(android_jar).exists():
        _, meta = observer.fail("Could not find `android.jar` - quitting LibScout scan-task!")
        return meta

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
    observer.update("Running scan...")
    stats = matcher.identify_libs(scan_task.scan.file.file_path)

    # 4. save stats to local file
    observer.update("Saving results of Libscout scan...")
    json_stats = export_app_stats(stats)
    json_out_path = scan.project.directory / f"libscout-{scan.file.internal_name}.json"
    with open(str(json_out_path), "w") as fp:
        json.dump(json_stats, fp)

    dependencies: dict[Package, Dependency] = {}
    # 5.1: Package-only matches
    observer.update("Matching package-only matches...")
    for key in stats.package_only_matches:
        group_id = stats.package_only_matches[key]
        artifact_id = None

        # We assume '::' is a separator that can be used to split groupID and artifactID
        if "::" in key:
            group_id, artifact_id = key.split("::", 1)

        try:
            package = Package.objects.get(group_id=group_id, artifact_id=artifact_id)
            if package not in dependencies:
                dependencies[package] = Dependency(pk=uuid.uuid4(), package=package)
        except (Package.DoesNotExist, Package.MultipleObjectsReturned):
            pass

    # 5.2 add partial matches
    observer.update("Matching full+partial matches...")
    for profile_match in stats.matches:
        # assert profile_match instanceof ProfileMatch
        best_match = profile_match.best_match
        if best_match and best_match.score > 0:
            args = {}
            if "::" in profile_match.lib_profile.name:
                (
                    args["group_id"],
                    args["artifact_id"],
                ) = profile_match.lib_profile.name.split("::", 1)
            else:
                args["name"] = profile_match.lib_profile.name

            try:
                version = profile_match.lib_profile.version
                package = Package.objects.get(**args)
                if package not in dependencies:
                    dependencies[package] = Dependency(
                        pk=uuid.uuid4(), package=package, version=version
                    )
                else:
                    # try to add version to dependency object
                    dependency = dependencies[package]
                    if str(dependency.version) < str(version):
                        dependency.version = version
            except (Package.DoesNotExist, Package.MultipleObjectsReturned):
                pass

    # 6. # Add all dependencies to the current scan if not already present
    present_packages = set(
        map(lambda x: x.package, Dependency.objects.filter(project=scan.project))
    )
    for package in dependencies:
        dependency = dependencies[package]
        if package in present_packages:
            dependencies.pop(package)
            continue  # just ignore duplicates

        dependency.project = scan.project
        dependency.scanner = scan_task.scanner

    Dependency.objects.bulk_create(list(dependencies.values()))
    _, meta = observer.success("Finished LibScout scan!")
    return meta
