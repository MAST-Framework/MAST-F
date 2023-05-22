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
from django import forms

from mastf.MASTF.models import Project
from .base import ModelField, ManyToManyField

__all__ = ["ScanForm"]


class ScanForm(forms.Form):
    project = ModelField(Project, required=False, max_length=64)
    origin = forms.CharField(max_length=32, required=False)
    source = forms.CharField(max_length=256, required=True)
    scan_type = forms.CharField(max_length=256, required=True)
    start_date = forms.DateField(required=False)
    status = forms.CharField(max_length=256, required=False)
    file_url = forms.CharField(max_length=512, required=False)

    projects = ManyToManyField(Project, required=False)
