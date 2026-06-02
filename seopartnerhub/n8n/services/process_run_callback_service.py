from __future__ import annotations

import hashlib
import hmac
import json
import logging
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from seopartnerhub.n8n.models import ProcessRun, RunStatus

logger = logging.getLogger(__name__)


class CallbackAuthError(Exception):
    """Raised when an inbound callback signature is invalid."""


class CallbackPayloadError(Exception):
    """Raised when a callback payload is malformed."""


class UnknownRunError(Exception):
    """Raised when a callback references an unknown run id."""


class TerminalRunConflictError(Exception):
    """Raised when a callback would mutate a terminal run with new data."""


class ProcessRunCallbackService:
    """Verify HMAC signatures and finalize :class:`ProcessRun` from n8n callbacks."""

    @staticmethod
    def verify_signature(*, raw_body: bytes, signature: str | None) -> None:
        if not signature:
            logger.warning("n8n_callback_missing_signature")
            msg = "missing_signature"
            raise CallbackAuthError(msg)
        secret = settings.N8N_CALLBACK_HMAC_SECRET.encode("utf-8")
        expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature.strip()):
            logger.warning("n8n_callback_invalid_signature")
            msg = "invalid_signature"
            raise CallbackAuthError(msg)

    @staticmethod
    def parse_payload(raw_body: bytes) -> dict:
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            logger.warning("n8n_callback_invalid_json")
            msg = "invalid_json"
            raise CallbackPayloadError(msg) from exc
        if not isinstance(data, dict):
            msg = "invalid_payload_root"
            raise CallbackPayloadError(msg)
        return data

    @classmethod
    @transaction.atomic
    def apply_callback(cls, *, payload: dict) -> ProcessRun:
        run_id = cls._extract_run_id(payload)
        status = cls._extract_status(payload)
        run = ProcessRun.objects.select_for_update().filter(pk=run_id).first()
        if run is None:
            logger.warning(
                "n8n_callback_unknown_run",
                extra={"run_id": str(run_id)},
            )
            msg = "unknown_run"
            raise UnknownRunError(msg)

        if run.is_terminal():
            logger.info(
                "n8n_callback_terminal_run_received",
                extra={"run_id": str(run_id), "current_status": run.status},
            )
            if run.status != status:
                msg = "terminal_run_conflict"
                raise TerminalRunConflictError(msg)
            return run

        result = payload.get("result")
        if result is not None and not isinstance(result, dict):
            msg = "invalid_result"
            raise CallbackPayloadError(msg)

        error_message = payload.get("error")
        if status == RunStatus.FAILED.value and not error_message:
            msg = "error_required_for_failed"
            raise CallbackPayloadError(msg)
        if error_message is not None and not isinstance(error_message, str):
            msg = "invalid_error_field"
            raise CallbackPayloadError(msg)

        run.status = status
        run.result_json = result if isinstance(result, dict) else None
        run.error_message = error_message if status == RunStatus.FAILED.value else ""
        run.finished_at = timezone.now()
        run.save(
            update_fields=[
                "status",
                "result_json",
                "error_message",
                "finished_at",
                "updated_at",
            ],
        )
        logger.info(
            "n8n_callback_run_completed",
            extra={
                "run_id": str(run_id),
                "process_id": run.process_id,
                "status": status,
            },
        )
        return run

    @staticmethod
    def _extract_run_id(payload: dict) -> UUID:
        raw = payload.get("runId")
        if not isinstance(raw, str):
            msg = "missing_run_id"
            raise CallbackPayloadError(msg)
        try:
            return UUID(raw)
        except ValueError as exc:
            msg = "invalid_run_id"
            raise CallbackPayloadError(msg) from exc

    @staticmethod
    def _extract_status(payload: dict) -> str:
        status = payload.get("status")
        if status not in {RunStatus.SUCCEEDED.value, RunStatus.FAILED.value}:
            msg = "invalid_status"
            raise CallbackPayloadError(msg)
        return status
