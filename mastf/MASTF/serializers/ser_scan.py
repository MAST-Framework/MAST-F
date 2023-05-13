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

from mastf.MASTF.models import Scan, namespace, ScanTask
from mastf.core.progress import PROGRESS

__all__ = ["ScanSerializer", "ScanTaskSerializer", "CeleryAsyncResultSerializer"]

logger = logging.getLogger(__name__)


class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = "__all__"


class CeleryAsyncResultSerializer(serializers.Serializer):
    def to_representation(self, instance: AsyncResult):
        if not instance:
            return {}

        if not isinstance(instance, (AsyncResult, str)):
            raise TypeError(
                f"Invalid input type for class {self.__class__}; expected AsyncResult, "
                "got {instance.__class__}!"
            )

        if isinstance(instance, str):
            instance = AsyncResult(instance)

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
            if isinstance(result, Exception):
                data.result = str(result)
            elif isinstance(result, dict):
                data.result = result.get(
                    "description", f"Task with id={instance.id} finished!"
                )
            else:
                data.result = str(result)

            data.progress.update({"current": 0, "percent": 100})

        return data


class ScanTaskSerializer(serializers.ModelSerializer):
    celery_id = CeleryAsyncResultSerializer(many=False)

    class Meta:
        model = ScanTask
        fields = "__all__"
