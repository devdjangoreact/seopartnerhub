from __future__ import annotations

from rest_framework import serializers

from seopartnerhub.n8n.models import ProcessRun


class ProcessRunSerializer(serializers.ModelSerializer):
    process = serializers.IntegerField(source="process_id", read_only=True)
    started_by = serializers.SerializerMethodField()

    class Meta:
        model = ProcessRun
        fields = (
            "id",
            "process",
            "status",
            "trigger_source",
            "settings_snapshot_json",
            "request_payload_json",
            "result_json",
            "error_message",
            "started_by",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_started_by(self, obj: ProcessRun) -> dict | None:
        if obj.started_by_id is None:
            return None
        return {
            "id": obj.started_by_id,
            "email": getattr(obj.started_by, "email", None),
        }
