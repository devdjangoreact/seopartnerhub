from __future__ import annotations

import logging

from celery import shared_task

from seopartnerhub.n8n.services.process_timeout_service import ProcessTimeoutService

logger = logging.getLogger(__name__)


@shared_task(
    name="seopartnerhub.n8n.tasks.mark_timed_out_process_runs",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def mark_timed_out_process_runs() -> int:
    """Mark long-running runs as ``timed_out``."""

    count = ProcessTimeoutService.sweep()
    logger.info("n8n_timeout_sweep_complete", extra={"count": count})
    return count
