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

from mastf.MASTF.models import Scan

__all__ = [
    "ScanSerializer",
    "CeleryStatusSerializer",
    "CeleryResultSerializer",
]


class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = "__all__"


class CeleryStatusSerializer(serializers.Serializer):
    pending = serializers.BooleanField(default=False, required=False)
    current = serializers.IntegerField(required=True)
    total = serializers.IntegerField(default=100, required=False)
    detail = serializers.CharField(default=None, required=False)
    complete = serializers.BooleanField(default=False, required=False)


class CeleryResultSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    status = CeleryStatusSerializer(required=True)

    @staticmethod # should be deprecated by now
    def empty() -> dict:
        # This method should be called whenever the celery worker has not been
        # started and a scan should be done
        return {
            "state": "PENDING",
            "status": {"pending": True, "detail": "Celery Worker not started"},
        }
