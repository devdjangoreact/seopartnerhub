from __future__ import annotations

from rest_framework import serializers

from seopartnerhub.n8n.models import Process


class ProcessUpdateSerializer(serializers.ModelSerializer):
    """Serializer for partial updates of mutable :class:`Process` fields.

    Schema-level validation of ``settings_json`` is delegated to
    :class:`seopartnerhub.n8n.services.process_configuration_service.ProcessConfigurationService`.
    """

    class Meta:
        model = Process
        fields = (
            "name",
            "is_active",
            "settings_json",
            "webhook_path",
            "schedule_cron",
        )
        extra_kwargs = {
            "name": {"required": False},
            "is_active": {"required": False},
            "settings_json": {"required": False},
            "webhook_path": {"required": False},
            "schedule_cron": {"required": False, "allow_null": True},
        }
