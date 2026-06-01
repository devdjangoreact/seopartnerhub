from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
from rest_framework.exceptions import ValidationError

from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTrigger
from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTriggerError
from seopartnerhub.n8n.models import RunStatus
from seopartnerhub.n8n.services.process_configuration_service import (
    ProcessConfigurationService,
)
from seopartnerhub.n8n.services.process_run_callback_service import CallbackPayloadError
from seopartnerhub.n8n.services.process_run_callback_service import (
    ProcessRunCallbackService,
)
from seopartnerhub.n8n.services.process_timeout_service import ProcessTimeoutService
from seopartnerhub.n8n.services.process_trigger_service import ProcessNotActiveError
from seopartnerhub.n8n.services.process_trigger_service import ProcessTriggerService
from seopartnerhub.n8n.services.sample_process_bootstrap_service import (
    SampleProcessBootstrapService,
)
from seopartnerhub.n8n.tests.factories import ProcessRunFactory
from seopartnerhub.n8n.tests.factories import TelegramProcessFactory
from seopartnerhub.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from seopartnerhub.n8n.schemas.json_value import JsonObject

pytestmark = pytest.mark.django_db


class _RecordingWebhook(WebhookTrigger):
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def trigger(self, *, webhook_path: str, payload: JsonObject) -> JsonObject:
        self.calls.append({"webhook_path": webhook_path, "payload": payload})
        return {}


class _FailingWebhook(WebhookTrigger):
    def trigger(self, *, webhook_path: str, payload: JsonObject) -> JsonObject:
        msg = "network_failure"
        raise WebhookTriggerError(msg)


# ---------------------------------------------------------------------------
# US2 service tests
# ---------------------------------------------------------------------------


class TestProcessConfigurationService:
    def test_invalid_settings_raise_and_preserve_previous(self):
        process = TelegramProcessFactory()
        original = dict(process.settings_json)
        with pytest.raises(ValidationError):
            ProcessConfigurationService.apply_partial_update(
                process=process,
                validated={"settings_json": {"chat_id": "", "message": ""}},
            )
        process.refresh_from_db()
        assert process.settings_json == original

    def test_valid_settings_applied_and_normalized(self):
        process = TelegramProcessFactory()
        ProcessConfigurationService.apply_partial_update(
            process=process,
            validated={
                "settings_json": {
                    "chat_id": "  @ch ",
                    "message": "hi",
                    "parse_mode": "HTML",
                },
            },
        )
        process.refresh_from_db()
        assert process.settings_json["chat_id"] == "@ch"
        assert process.settings_json["parse_mode"] == "HTML"
        assert process.settings_json["disable_web_page_preview"] is False


# ---------------------------------------------------------------------------
# US3 service tests
# ---------------------------------------------------------------------------


class TestProcessTriggerService:
    def test_inactive_process_raises(self):
        process = TelegramProcessFactory(is_active=False)
        service = ProcessTriggerService(webhook_trigger=_RecordingWebhook())
        with pytest.raises(ProcessNotActiveError):
            service.trigger_manual(process=process, user=UserFactory())

    def test_network_failure_marks_run_failed(self):
        process = TelegramProcessFactory()
        service = ProcessTriggerService(webhook_trigger=_FailingWebhook())
        run = service.trigger_manual(process=process, user=UserFactory())
        run.refresh_from_db()
        assert run.status == RunStatus.FAILED.value
        assert run.error_message
        assert run.finished_at is not None


class TestProcessTimeoutService:
    def test_old_running_runs_marked_timed_out(self):
        process = TelegramProcessFactory()
        old = ProcessRunFactory(
            process=process,
            started_at=timezone.now() - timedelta(hours=1),
            status=RunStatus.RUNNING.value,
        )
        fresh = ProcessRunFactory(
            process=process,
            started_at=timezone.now(),
            status=RunStatus.RUNNING.value,
        )

        ProcessTimeoutService.sweep(timeout_seconds=900)

        old.refresh_from_db()
        fresh.refresh_from_db()
        assert old.status == RunStatus.TIMED_OUT.value
        assert old.finished_at is not None
        assert fresh.status == RunStatus.RUNNING.value


class TestProcessRunCallbackService:
    def test_failed_payload_requires_error(self):
        run = ProcessRunFactory()
        with pytest.raises(CallbackPayloadError):
            ProcessRunCallbackService.apply_callback(
                payload={"runId": str(run.id), "status": RunStatus.FAILED.value},
            )


# ---------------------------------------------------------------------------
# US4 + Phase 7 service tests
# ---------------------------------------------------------------------------


class TestSampleProcessBootstrapService:
    def test_idempotent_creation(self):
        first = SampleProcessBootstrapService.ensure_telegram_sample()
        second = SampleProcessBootstrapService.ensure_telegram_sample()
        assert first.pk == second.pk

    def test_sample_settings_match_telegram_schema(self):
        process = SampleProcessBootstrapService.ensure_telegram_sample()
        assert "chat_id" in process.settings_json
        assert "message" in process.settings_json


class TestCronScheduleSync:
    def test_cron_schedule_creates_or_updates_periodic_task(self):
        process = TelegramProcessFactory(schedule_cron="*/5 * * * *")
        ProcessConfigurationService.apply_partial_update(
            process=process,
            validated={"schedule_cron": "*/10 * * * *"},
        )
        task = PeriodicTask.objects.filter(
            name=f"n8n.scheduled_trigger.process_{process.pk}",
        ).first()
        assert task is not None
        assert task.crontab.minute == "*/10"

    def test_cron_invalid_field_count_skips_periodic_task(self):
        process = TelegramProcessFactory()
        with pytest.raises(DjangoValidationError):
            ProcessConfigurationService.apply_partial_update(
                process=process,
                validated={"schedule_cron": "*/5 *"},
            )
