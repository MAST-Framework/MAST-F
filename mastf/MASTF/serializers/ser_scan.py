from rest_framework import serializers

from mastf.MASTF.models import Scan

__all__ = [
    'ScanSerializer',
    'CeleryStatusSerializer',
    'CeleryResultSerializer',
]

class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = '__all__'


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

    @staticmethod
    def empty() -> dict:
        # This method should be called whenever the celery worker has not been
        # started and a scan should be done
        return {
            "state": "PENDING",
            "status": {
                "pending": True, "detail": "Celery Worker not started"
            }
        }