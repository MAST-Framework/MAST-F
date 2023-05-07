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
from rest_framework import serializers

from mastf.MASTF.models import (
    Host,
    DataCollectionGroup,
    CipherSuite,
    TLS,
    HostTemplate
)

from .base import ManyToManyField, ManyToManySerializer

__all__ = [
    "DataCollectionGroupSerializer",
    "TLSSerializer",
    "CipherSuiteSerializer",
    "HostSerializer",
    "HostTemplateSerializer",
]


class DataCollectionGroupSerializer(ManyToManySerializer):
    rel_fields = ["hosts"]
    hosts = ManyToManyField(Host)

    class Meta:
        model = DataCollectionGroup
        fields = "__all__"


class TLSSerializer(ManyToManySerializer):
    rel_fields = ["hosts"]
    hosts = ManyToManyField(Host)

    class Meta:
        model = TLS
        fields = "__all__"


class CipherSuiteSerializer(ManyToManySerializer):
    rel_fields = ["hosts"]
    hosts = ManyToManyField(Host)

    class Meta:
        model = CipherSuite
        fields = "__all__"


class HostTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostTemplate
        fields = "__all__"


class HostSerializer(ManyToManySerializer):
    rel_fields = ["tlsversions", "suites", "collected_data"]
    tlsversions = ManyToManyField(TLS)
    suites = ManyToManyField(CipherSuite)
    collected_data = ManyToManyField(DataCollectionGroup)
    template = HostTemplateSerializer(many=False)

    class Meta:
        model = Host
        fields = "__all__"
