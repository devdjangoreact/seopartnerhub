from __future__ import annotations

import logging

from seopartnerhub.n8n.models import Process
from seopartnerhub.n8n.schemas.process_kind import ProcessKind

logger = logging.getLogger(__name__)


class SampleProcessBootstrapService:
    """Idempotently provision the canonical Telegram-post sample process."""

    SAMPLE_NAME = "Telegram post via BotFather"
    SAMPLE_WEBHOOK_PATH = "/seopartnerhub/telegram-post"
    SAMPLE_SETTINGS = {
        "chat_id": "@example_channel",
        "message": "Hello from SEOPartnerHub via n8n!",
        "parse_mode": None,
        "disable_web_page_preview": False,
    }

    @classmethod
    def ensure_telegram_sample(cls) -> Process:
        process, created = Process.objects.get_or_create(
            kind=ProcessKind.TELEGRAM_POST.value,
            name=cls.SAMPLE_NAME,
            defaults={
                "is_active": True,
                "settings_json": cls.SAMPLE_SETTINGS,
                "webhook_path": cls.SAMPLE_WEBHOOK_PATH,
                "schedule_cron": "",
            },
        )
        if created:
            logger.info(
                "n8n_sample_process_created",
                extra={"process_id": process.pk, "kind": process.kind},
            )
        return process
