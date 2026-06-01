from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import transaction
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask
from pydantic import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from seopartnerhub.n8n.schemas.schema_registry import SchemaRegistry

if TYPE_CHECKING:
    from collections.abc import Mapping

    from seopartnerhub.n8n.models import Process
    from seopartnerhub.n8n.schemas.json_value import JsonObject

logger = logging.getLogger(__name__)

CRON_FIELD_COUNT = 5


class ProcessConfigurationService:
    """Update mutable :class:`Process` fields with typed-schema validation."""

    @staticmethod
    @transaction.atomic
    def apply_partial_update(
        *,
        process: Process,
        validated: Mapping[str, object],
    ) -> Process:
        if "settings_json" in validated:
            settings_value = validated["settings_json"]
            if not isinstance(settings_value, dict):
                logger.warning(
                    "n8n_process_settings_invalid_shape",
                    extra={"process_id": process.pk},
                )
                raise DRFValidationError(
                    {"settings_json": ["settings_json must be a JSON object."]},
                )
            normalized = ProcessConfigurationService._validate_settings(
                kind=process.kind,
                payload=settings_value,
                process_id=process.pk,
            )
            process.settings_json = normalized

        for field in ("name", "is_active", "webhook_path", "schedule_cron"):
            if field in validated:
                setattr(process, field, validated[field])

        ProcessConfigurationService._sync_schedule(process)
        process.full_clean(exclude=("settings_json",))
        process.save()
        logger.info(
            "n8n_process_updated",
            extra={
                "process_id": process.pk,
                "fields": sorted(validated.keys()),
            },
        )
        return process

    @staticmethod
    def _validate_settings(
        *,
        kind: str,
        payload: JsonObject,
        process_id: int | None,
    ) -> JsonObject:
        try:
            return SchemaRegistry.validate(kind, payload)
        except ValidationError as exc:
            logger.warning(
                "n8n_process_settings_rejected",
                extra={
                    "process_id": process_id,
                    "kind": kind,
                    "errors": exc.errors(include_url=False),
                },
            )
            field_errors: dict[str, list[str]] = {}
            for err in exc.errors(include_url=False):
                key = ".".join(str(p) for p in err["loc"]) or "settings_json"
                field_errors.setdefault(key, []).append(err["msg"])
            raise DRFValidationError({"settings_json": field_errors}) from exc

    @staticmethod
    def _sync_schedule(process: Process) -> None:
        """Sync the ``django-celery-beat`` periodic task for ``process``."""

        task_name = f"n8n.scheduled_trigger.process_{process.pk}"
        cron = (process.schedule_cron or "").strip()

        if not cron or not process.is_active:
            PeriodicTask.objects.filter(name=task_name).delete()
            return

        parts = cron.split()
        if len(parts) != CRON_FIELD_COUNT:
            return
        minute, hour, day_of_month, month_of_year, day_of_week = parts
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            day_of_week=day_of_week,
        )
        PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults={
                "crontab": schedule,
                "task": "seopartnerhub.n8n.tasks.trigger_scheduled_process",
                "args": f"[{process.pk}]",
                "enabled": True,
            },
        )
