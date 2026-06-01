from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from seopartnerhub.n8n.models import RunStatus
from seopartnerhub.n8n.selectors.process_run_selector import ProcessRunSelector

logger = logging.getLogger(__name__)


class ProcessTimeoutService:
    """Mark long-running runs as ``timed_out``."""

    @staticmethod
    @transaction.atomic
    def sweep(*, timeout_seconds: int | None = None) -> int:
        seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else int(settings.N8N_PROCESS_RUN_TIMEOUT_SECONDS)
        )
        threshold = timezone.now() - timedelta(seconds=seconds)
        runs = ProcessRunSelector.running_started_before(threshold).select_for_update(
            skip_locked=True,
        )
        count = 0
        for run in runs:
            run.status = RunStatus.TIMED_OUT.value
            run.error_message = "run_timed_out"
            run.finished_at = timezone.now()
            run.save(
                update_fields=[
                    "status",
                    "error_message",
                    "finished_at",
                    "updated_at",
                ],
            )
            logger.warning(
                "n8n_run_timed_out",
                extra={
                    "run_id": str(run.id),
                    "process_id": run.process_id,
                    "started_at": run.started_at.isoformat(),
                },
            )
            count += 1
        return count
