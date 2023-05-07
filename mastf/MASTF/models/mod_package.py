# This file is part of MAST-F's Frontend API
# Copyright (C) 2023  MatrixEditor, Janbehere1
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
from django.db import models

from mastf.MASTF.utils.enum import Platform, PackageType, Relation, Severity

from .base import Project
from .mod_scan import Scanner

__all__ = ["Package", "PackageVulnerability", "Dependency"]


class Package(models.Model):
    package_uuid = models.UUIDField(max_length=36, primary_key=True)
    name = models.CharField(max_length=512, null=True)
    artifact_id = models.CharField(max_length=512, null=True, blank=True)
    group_id = models.CharField(max_length=512, null=True, blank=True)
    type = models.CharField(
        default=PackageType.NONE, choices=PackageType.choices, max_length=256
    )
    platform = models.CharField(
        default=Platform.UNKNOWN, choices=Platform.choices, max_length=256
    )


class PackageVulnerability(models.Model):
    identifier = models.UUIDField(max_length=36, primary_key=True)
    cve_id = models.CharField(max_length=256, null=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    version = models.CharField(max_length=512, null=True)
    severity = models.CharField(
        max_length=32, choices=Severity.choices, default=Severity.NONE
    )


class Dependency(models.Model):
    dependency_uuid = models.CharField(max_length=72, primary_key=True)  # UUID*2
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    relation = models.CharField(
        default=Relation.DIRECT, choices=Relation.choices, max_length=256
    )
    scanner = models.ForeignKey(Scanner, models.CASCADE)
    outdated = models.CharField(max_length=512, null=True, blank=True)
    version = models.CharField(max_length=512, blank=True)
    license = models.CharField(max_length=256, null=True, blank=True)

    @property
    def vulnerabilities(self) -> models.QuerySet:
        return PackageVulnerability.objects.filter(
            package=self.package, version=self.version
        )
