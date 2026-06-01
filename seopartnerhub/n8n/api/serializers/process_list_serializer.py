from __future__ import annotations

from rest_framework import serializers


class LatestRunSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField(allow_null=True)
    status = serializers.CharField(allow_null=True)
    started_at = serializers.DateTimeField(allow_null=True)
    finished_at = serializers.DateTimeField(allow_null=True)


class ProcessListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    kind = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    schedule_cron = serializers.CharField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True)
    latest_run = serializers.SerializerMethodField()

    def get_latest_run(self, obj) -> dict | None:
        run_id = getattr(obj, "latest_run_id", None)
        if run_id is None:
            return None
        return LatestRunSummarySerializer(
            {
                "id": run_id,
                "status": getattr(obj, "latest_run_status", None),
                "started_at": getattr(obj, "latest_run_started_at", None),
                "finished_at": getattr(obj, "latest_run_finished_at", None),
            },
        ).data
