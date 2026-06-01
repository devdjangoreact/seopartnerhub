from __future__ import annotations

import logging

from celery import shared_task

from seopartnerhub.n8n.integrations.n8n_webhook_client import N8nWebhookClient
from seopartnerhub.n8n.models import Process
from seopartnerhub.n8n.services.process_trigger_service import ProcessTriggerService

logger = logging.getLogger(__name__)


@shared_task(
    name="seopartnerhub.n8n.tasks.trigger_scheduled_process",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def trigger_scheduled_process(process_id: int) -> None:
    """Celery task that triggers a process on its cron schedule."""

    process = Process.objects.filter(pk=process_id).first()
    if process is None:
        logger.warning(
            "n8n_scheduled_process_missing",
            extra={"process_id": process_id},
        )
        return
    service = ProcessTriggerService(webhook_trigger=N8nWebhookClient())
    run = service.trigger_scheduled(process=process)
    logger.info(
        "n8n_scheduled_process_dispatched",
        extra={
            "process_id": process_id,
            "run_id": str(run.id) if run else None,
        },
    )
