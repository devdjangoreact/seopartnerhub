from __future__ import annotations

from django.contrib import admin

from seopartnerhub.n8n.integrations.n8n_webhook_client import N8nWebhookClient
from seopartnerhub.n8n.models import Process
from seopartnerhub.n8n.models import ProcessRun
from seopartnerhub.n8n.services.process_trigger_service import ProcessTriggerService


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "kind", "is_active", "schedule_cron", "updated_at")
    list_filter = ("kind", "is_active")
    search_fields = ("name", "webhook_path")
    readonly_fields = ("created_at", "updated_at")
    actions = ("trigger_selected_processes",)

    @admin.action(description="Trigger selected processes manually")
    def trigger_selected_processes(self, request, queryset):
        service = ProcessTriggerService(webhook_trigger=N8nWebhookClient())
        triggered = 0
        for process in queryset:
            if not process.is_active:
                continue
            service.trigger_manual(process=process, user=request.user)
            triggered += 1
        self.message_user(request, f"Triggered {triggered} process(es).")


@admin.register(ProcessRun)
class ProcessRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "process",
        "status",
        "trigger_source",
        "started_by",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "trigger_source")
    search_fields = ("id", "process__name")
    readonly_fields = (
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
