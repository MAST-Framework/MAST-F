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
from django import forms

from mastf.MASTF.models import Package, Project, Scanner

from .base import ModelField

__all__ = ["PackageForm", "PackageVulnerabilityForm", "DependencyForm"]


class PackageForm(forms.Form):
    name = forms.CharField(max_length=512, required=True)
    artifact_id = forms.CharField(max_length=512, required=False)
    group_id = forms.CharField(max_length=512, required=False)
    type = forms.CharField(max_length=256, required=True)
    platform = forms.CharField(max_length=256, required=True)


class PackageVulnerabilityForm(forms.Form):
    cve_id = forms.CharField(max_length=256, required=True)
    package = ModelField(Package, max_length=72, required=True)
    version = forms.CharField(max_length=512, required=True)
    severity = forms.CharField(max_length=32, required=False)


class DependencyForm(forms.Form):
    package = ModelField(Package, max_length=36, required=True)
    project = ModelField(Project, max_length=256, required=True)
    relation = forms.CharField(
        max_length=256, required=False
    )  # maybe add enum validator
    scanner = ModelField(Scanner, max_length=256, required=True)
    outdated = forms.CharField(max_length=512, required=False)
    version = forms.CharField(max_length=512, required=False)
    license = forms.CharField(max_length=256, required=False)
