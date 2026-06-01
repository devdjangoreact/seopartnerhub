from __future__ import annotations

import uuid
from datetime import UTC
from datetime import datetime

from factory import LazyFunction
from factory import SubFactory
from factory.django import DjangoModelFactory

from seopartnerhub.n8n.models import Process
from seopartnerhub.n8n.models import ProcessRun
from seopartnerhub.n8n.models import RunStatus
from seopartnerhub.n8n.models import TriggerSource
from seopartnerhub.n8n.schemas.process_kind import ProcessKind
from seopartnerhub.users.tests.factories import UserFactory


class TelegramProcessFactory(DjangoModelFactory[Process]):
    name = "Telegram post via BotFather"
    kind = ProcessKind.TELEGRAM_POST.value
    is_active = True
    webhook_path = "/telegram-post"
    schedule_cron = ""

    class Meta:
        model = Process

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs.setdefault(
            "settings_json",
            {
                "chat_id": "@example_channel",
                "message": "Hello from SEOPartnerHub!",
                "parse_mode": None,
                "disable_web_page_preview": False,
            },
        )
        return super()._create(model_class, *args, **kwargs)


class ProcessRunFactory(DjangoModelFactory[ProcessRun]):
    id = LazyFunction(uuid.uuid4)
    process = SubFactory(TelegramProcessFactory)
    status = RunStatus.RUNNING.value
    trigger_source = TriggerSource.MANUAL.value
    started_by = SubFactory(UserFactory)
    started_at = LazyFunction(lambda: datetime.now(tz=UTC))

    class Meta:
        model = ProcessRun

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs.setdefault("settings_snapshot_json", {})
        kwargs.setdefault("request_payload_json", {})
        return super()._create(model_class, *args, **kwargs)
