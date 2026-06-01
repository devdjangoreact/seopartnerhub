from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTrigger
from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTriggerError
from seopartnerhub.n8n.models import Process
from seopartnerhub.n8n.models import ProcessRun
from seopartnerhub.n8n.models import RunStatus
from seopartnerhub.n8n.models import TriggerSource

if TYPE_CHECKING:
    from seopartnerhub.n8n.schemas.json_value import JsonObject
    from seopartnerhub.users.models import User

logger = logging.getLogger(__name__)


class ProcessNotActiveError(Exception):
    """Raised when attempting to trigger a deactivated process."""


class ProcessTriggerService:
    """Trigger processes manually or on schedule."""

    def __init__(self, *, webhook_trigger: WebhookTrigger) -> None:
        self._webhook = webhook_trigger

    def trigger_manual(
        self,
        *,
        process: Process,
        user: User | None,
    ) -> ProcessRun:
        if not process.is_active:
            logger.warning(
                "n8n_trigger_rejected_inactive",
                extra={"process_id": process.pk},
            )
            msg = "process_not_active"
            raise ProcessNotActiveError(msg)
        return self._trigger(
            process=process,
            user=user,
            source=TriggerSource.MANUAL.value,
        )

    def trigger_scheduled(self, *, process: Process) -> ProcessRun | None:
        if not process.is_active:
            logger.info(
                "n8n_scheduled_trigger_skipped_inactive",
                extra={"process_id": process.pk},
            )
            return None
        return self._trigger(
            process=process,
            user=None,
            source=TriggerSource.SCHEDULED.value,
        )

    def _trigger(
        self,
        *,
        process: Process,
        user: User | None,
        source: str,
    ) -> ProcessRun:
        run_id = uuid.uuid4()
        snapshot: JsonObject = dict(process.settings_json or {})
        payload: JsonObject = {
            "run_id": str(run_id),
            "process_id": process.pk,
            "kind": process.kind,
            "settings": snapshot,
            "trigger_source": source,
        }
        with transaction.atomic():
            run = ProcessRun.objects.create(
                id=run_id,
                process=process,
                status=RunStatus.RUNNING.value,
                trigger_source=source,
                settings_snapshot_json=snapshot,
                request_payload_json=payload,
                started_by=user,
                started_at=timezone.now(),
            )
        logger.info(
            "n8n_process_triggered",
            extra={
                "process_id": process.pk,
                "run_id": str(run_id),
                "source": source,
                "user_id": getattr(user, "id", None),
            },
        )
        try:
            self._webhook.trigger(
                webhook_path=process.webhook_path,
                payload=payload,
            )
        except WebhookTriggerError as exc:
            logger.exception(
                "n8n_trigger_webhook_failed",
                extra={"run_id": str(run_id), "process_id": process.pk},
            )
            self._mark_failed(run, str(exc) or "n8n_trigger_failed")
            run.refresh_from_db()
        return run

    @staticmethod
    def _mark_failed(run: ProcessRun, error_message: str) -> None:
        ProcessRun.objects.filter(pk=run.pk, status=RunStatus.RUNNING.value).update(
            status=RunStatus.FAILED.value,
            error_message=error_message,
            finished_at=timezone.now(),
        )
