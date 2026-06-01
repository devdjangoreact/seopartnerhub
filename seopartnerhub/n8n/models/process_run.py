from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class RunStatus(models.TextChoices):
    RUNNING = "running", "Running"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    TIMED_OUT = "timed_out", "Timed out"


class TriggerSource(models.TextChoices):
    MANUAL = "manual", "Manual"
    SCHEDULED = "scheduled", "Scheduled"


class ProcessRun(models.Model):
    """One execution attempt of a :class:`Process`."""

    TERMINAL_STATUSES = frozenset(
        {RunStatus.SUCCEEDED.value, RunStatus.FAILED.value, RunStatus.TIMED_OUT.value},
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    process = models.ForeignKey(
        "n8n.Process",
        on_delete=models.PROTECT,
        related_name="runs",
    )
    status = models.CharField(
        max_length=16,
        choices=RunStatus.choices,
        default=RunStatus.RUNNING,
    )
    trigger_source = models.CharField(
        max_length=16,
        choices=TriggerSource.choices,
        default=TriggerSource.MANUAL,
    )
    settings_snapshot_json = models.JSONField(default=dict)
    request_payload_json = models.JSONField(default=dict)
    result_json = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, default="")
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="n8n_started_runs",
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "n8n_process_run"
        ordering = ("-started_at",)
        indexes = [
            models.Index(fields=["process", "-started_at"], name="n8n_run_history_idx"),
            models.Index(fields=["status"], name="n8n_run_status_idx"),
            models.Index(fields=["started_at"], name="n8n_run_started_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.process_id}:{self.id}"

    def is_terminal(self) -> bool:
        return self.status in self.TERMINAL_STATUSES
