from __future__ import annotations

from django.core.validators import RegexValidator
from django.db import models

from seopartnerhub.n8n.schemas.process_kind import ProcessKind

CRON_FIELD_PATTERN = r"^\s*$|^\s*\S+\s+\S+\s+\S+\s+\S+\s+\S+\s*$"
cron_validator = RegexValidator(
    regex=CRON_FIELD_PATTERN,
    message="schedule_cron must be empty or contain exactly five fields",
)


class Process(models.Model):
    """Automation process exposed to authenticated users."""

    name = models.CharField(max_length=255)
    kind = models.CharField(
        max_length=64,
        choices=ProcessKind.choices,
        default=ProcessKind.TELEGRAM_POST,
    )
    is_active = models.BooleanField(default=True)
    settings_json = models.JSONField(default=dict)
    webhook_path = models.CharField(max_length=512)
    schedule_cron = models.CharField(
        max_length=128,
        blank=True,
        default="",
        validators=[cron_validator],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "n8n_process"
        ordering = ("name",)
        indexes = [
            models.Index(fields=["kind"], name="n8n_proc_kind_idx"),
            models.Index(fields=["is_active"], name="n8n_proc_active_idx"),
            models.Index(fields=["schedule_cron"], name="n8n_proc_cron_idx"),
        ]

    def __str__(self) -> str:
        return self.name
