from __future__ import annotations

from rest_framework import serializers

from seopartnerhub.n8n.api.serializers.process_list_serializer import (
    LatestRunSummarySerializer,
)
from seopartnerhub.n8n.models import Process


class ProcessDetailSerializer(serializers.ModelSerializer):
    latest_run = serializers.SerializerMethodField()

    class Meta:
        model = Process
        fields = (
            "id",
            "name",
            "kind",
            "is_active",
            "settings_json",
            "webhook_path",
            "schedule_cron",
            "created_at",
            "updated_at",
            "latest_run",
        )
        read_only_fields = fields

    def get_latest_run(self, obj: Process) -> dict | None:
        run_id = getattr(obj, "latest_run_id", None)
        if run_id is not None:
            return LatestRunSummarySerializer(
                {
                    "id": run_id,
                    "status": getattr(obj, "latest_run_status", None),
                    "started_at": getattr(obj, "latest_run_started_at", None),
                    "finished_at": getattr(obj, "latest_run_finished_at", None),
                },
            ).data
        latest = obj.runs.order_by("-started_at").first()
        if latest is None:
            return None
        return LatestRunSummarySerializer(
            {
                "id": latest.id,
                "status": latest.status,
                "started_at": latest.started_at,
                "finished_at": latest.finished_at,
            },
        ).data
