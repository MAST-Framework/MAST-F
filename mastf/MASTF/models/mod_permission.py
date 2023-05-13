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
from uuid import uuid4
from django.db import models

from mastf.MASTF.utils.enum import ProtectionLevel

from .mod_finding import AbstractBaseFinding, FindingTemplate

__all__ = ["AppPermission", "PermissionFinding"]


class AppPermission(models.Model):
    permission_uuid = models.UUIDField(primary_key=True)
    identifier = models.CharField(max_length=256, null=False)
    name = models.CharField(max_length=256, null=True)
    # maybe add choices here
    protection_level = models.TextField(blank=True)
    dangerous = models.BooleanField(default=False)
    group = models.CharField(max_length=256, null=True)

    short_description = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)

    risk = models.TextField(blank=True)

    @property
    def plevel_status(self) -> dict:
        plevel = {}
        colors = ProtectionLevel.colors()
        for level in self.protection_level.split(","):
            found = False
            level = str(level).capitalize()
            for color, values in colors.items():
                if level in values:
                    plevel[level] = color
                    found = True
                    break

            if not found:
                plevel[level] = "secondary"
        return plevel

    @staticmethod
    def create_unknown(identifier, protection_level) -> "AppPermission":
        return AppPermission.objects.create(
            pk=uuid4(),
            identifier=identifier,
            name=identifier.split(".")[-1].lower().capitalize(),
            protection_level=protection_level,
            dangerous="dangerous" in protection_level.lower(),
            short_description="Dynamic generated description. Please edit the short and long description"
            "in the plugins-context of your site.",
        )


class PermissionFinding(AbstractBaseFinding):
    permission = models.ForeignKey(AppPermission, null=True, on_delete=models.SET_NULL)
