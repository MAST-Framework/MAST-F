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

from rest_framework import serializers
from celery.result import AsyncResult
from celery.app.task import states

from mastf.MASTF.models import Scan, namespace
from mastf.core.progress import PROGRESS

__all__ = [
    "ScanSerializer",
    "CeleryStatusSerializer",
    "CeleryResultSerializer",
]

logger = logging.getLogger(__name__)


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

    def to_representation(self, instance):
        logger.debug("[%s] Writing value: %s", self.__class__.__name__, str(instance))
        if isinstance(instance, str):
            return {"current": 0, "detail": instance}

        return super().to_representation(instance)


class CeleryResultSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    info = CeleryStatusSerializer(required=True)

    @staticmethod  # should be deprecated by now
    def empty() -> dict:
        # This method should be called whenever the celery worker has not been
        # started and a scan should be done
        return {
            "state": "PENDING",
            "status": {"pending": True, "detail": "Celery Worker not started"},
        }


class CeleryAsyncResultSerializer(serializers.Serializer):
    def to_representation(self, instance: AsyncResult):
        if not isinstance(instance, AsyncResult):
            raise TypeError(
                f"Invalid input type for class {self.__class__}; expected AsyncResult, "
                "got {instance.__class__}!"
            )

        data = namespace(
            id=instance.id,
            state=instance.state,
            complete=False,
            success=False,
            progress={},
        )

        meta: dict = instance._get_task_meta()
        state = meta.get("status", None)
        result = meta["result"]

        data.state = state
        if state == PROGRESS:
            data.progress = result

        elif state in (states.PENDING, states.STARTED):
            data.progress.update(
                {"pending": True, "current": 0, "total": 100, "percent": 0}
            )

        elif state in (states.SUCCESS, states.FAILURE):
            success = instance.successful()
            data.complete = True
            data.success = success
            data.result = f"Task with id={instance.id} finished!"
            data.progress.update(
                {"current": 0, "percent": 100}
            )

        return data