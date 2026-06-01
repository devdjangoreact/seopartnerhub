from __future__ import annotations

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import seopartnerhub.n8n.models.process


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Process",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "kind",
                    models.CharField(
                        choices=[("telegram_post", "Telegram post")],
                        default="telegram_post",
                        max_length=64,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("settings_json", models.JSONField(default=dict)),
                ("webhook_path", models.CharField(max_length=512)),
                (
                    "schedule_cron",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=128,
                        validators=[seopartnerhub.n8n.models.process.cron_validator],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "n8n_process",
                "ordering": ("name",),
            },
        ),
        migrations.AddIndex(
            model_name="process",
            index=models.Index(fields=["kind"], name="n8n_proc_kind_idx"),
        ),
        migrations.AddIndex(
            model_name="process",
            index=models.Index(fields=["is_active"], name="n8n_proc_active_idx"),
        ),
        migrations.AddIndex(
            model_name="process",
            index=models.Index(fields=["schedule_cron"], name="n8n_proc_cron_idx"),
        ),
        migrations.CreateModel(
            name="ProcessRun",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("running", "Running"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                            ("timed_out", "Timed out"),
                        ],
                        default="running",
                        max_length=16,
                    ),
                ),
                (
                    "trigger_source",
                    models.CharField(
                        choices=[("manual", "Manual"), ("scheduled", "Scheduled")],
                        default="manual",
                        max_length=16,
                    ),
                ),
                ("settings_snapshot_json", models.JSONField(default=dict)),
                ("request_payload_json", models.JSONField(default=dict)),
                ("result_json", models.JSONField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True, default="")),
                ("started_at", models.DateTimeField()),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "process",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="runs",
                        to="n8n.process",
                    ),
                ),
                (
                    "started_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="n8n_started_runs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "n8n_process_run",
                "ordering": ("-started_at",),
            },
        ),
        migrations.AddIndex(
            model_name="processrun",
            index=models.Index(
                fields=["process", "-started_at"],
                name="n8n_run_history_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="processrun",
            index=models.Index(fields=["status"], name="n8n_run_status_idx"),
        ),
        migrations.AddIndex(
            model_name="processrun",
            index=models.Index(fields=["started_at"], name="n8n_run_started_idx"),
        ),
    ]
