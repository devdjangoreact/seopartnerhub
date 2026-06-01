from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTrigger
from seopartnerhub.n8n.models import Process
from seopartnerhub.n8n.models import ProcessRun
from seopartnerhub.n8n.models import RunStatus
from seopartnerhub.n8n.models import TriggerSource
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
        return {"accepted": True}


@pytest.fixture
def authed_client():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def anon_client():
    return APIClient()


def _list_url() -> str:
    return reverse("api:n8n-process-list")


def _detail_url(process: Process) -> str:
    return reverse("api:n8n-process-detail", args=[process.pk])


def _trigger_url(process: Process) -> str:
    return reverse("api:n8n-process-trigger", args=[process.pk])


def _runs_url(process: Process) -> str:
    return reverse("api:n8n-process-runs", args=[process.pk])


def _run_detail_url(run: ProcessRun) -> str:
    return reverse("api:n8n-run-detail", args=[run.pk])


def _callback_url() -> str:
    return reverse("n8n:callback-runs")


def _sign(body: bytes) -> str:
    secret = settings.N8N_CALLBACK_HMAC_SECRET.encode("utf-8")
    return hmac.new(secret, body, hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# US1: Browse processes
# ---------------------------------------------------------------------------


class TestProcessListAndRetrieve:
    def test_unauthenticated_list_rejected(self, anon_client):
        response = anon_client.get(_list_url())
        assert response.status_code in {
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        }

    def test_unauthenticated_retrieve_rejected(self, anon_client):
        process = TelegramProcessFactory()
        response = anon_client.get(_detail_url(process))
        assert response.status_code in {
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        }

    def test_authenticated_list_with_latest_run_summary(self, authed_client):
        client, _ = authed_client
        process = TelegramProcessFactory()
        run = ProcessRunFactory(
            process=process,
            status=RunStatus.SUCCEEDED.value,
            finished_at=timezone.now(),
        )

        response = client.get(_list_url())
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        results = data.get("results", data) if isinstance(data, dict) else data
        assert isinstance(results, list)
        item = next(r for r in results if r["id"] == process.pk)
        assert item["name"] == process.name
        assert item["kind"] == process.kind
        latest = item["latest_run"]
        assert latest is not None
        assert latest["id"] == str(run.id)
        assert latest["status"] == RunStatus.SUCCEEDED.value

    def test_authenticated_retrieve_with_settings_and_latest_run(self, authed_client):
        client, _ = authed_client
        process = TelegramProcessFactory()
        run = ProcessRunFactory(process=process)

        response = client.get(_detail_url(process))
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["id"] == process.pk
        assert body["settings_json"]["chat_id"] == process.settings_json["chat_id"]
        assert body["webhook_path"] == process.webhook_path
        assert body["latest_run"]["id"] == str(run.id)


# ---------------------------------------------------------------------------
# US2: View and edit configuration
# ---------------------------------------------------------------------------


class TestProcessConfigUpdate:
    def test_valid_settings_update_persists(self, authed_client):
        client, _ = authed_client
        process = TelegramProcessFactory()
        new_settings = {
            "chat_id": "@new_channel",
            "message": "Updated message",
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        response = client.patch(
            _detail_url(process),
            data={"settings_json": new_settings, "name": "Renamed"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        process.refresh_from_db()
        assert process.settings_json["chat_id"] == "@new_channel"
        assert process.settings_json["parse_mode"] == "HTML"
        assert process.name == "Renamed"

    def test_invalid_telegram_settings_rejected_and_preserves_old(
        self,
        authed_client,
    ):
        client, _ = authed_client
        process = TelegramProcessFactory()
        original = dict(process.settings_json)

        response = client.patch(
            _detail_url(process),
            data={"settings_json": {"chat_id": "", "message": ""}},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        process.refresh_from_db()
        assert process.settings_json == original


# ---------------------------------------------------------------------------
# US3: Manual trigger and run history + callback
# ---------------------------------------------------------------------------


class TestProcessTrigger:
    def test_manual_trigger_creates_running_run(
        self,
        authed_client,
        monkeypatch,
    ):
        client, user = authed_client
        process = TelegramProcessFactory()
        recorder = _RecordingWebhook()
        monkeypatch.setattr(
            "seopartnerhub.n8n.api.views.process_view_set.N8nWebhookClient",
            lambda *a, **kw: recorder,
        )

        response = client.post(_trigger_url(process), data={}, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        body = response.json()
        run_id = uuid.UUID(body["id"])
        run = ProcessRun.objects.get(pk=run_id)
        assert run.status == RunStatus.RUNNING.value
        assert run.trigger_source == TriggerSource.MANUAL.value
        assert run.started_by_id == user.id
        assert recorder.calls
        assert recorder.calls[0]["webhook_path"] == process.webhook_path

    def test_trigger_rejected_when_inactive(self, authed_client, monkeypatch):
        client, _ = authed_client
        process = TelegramProcessFactory(is_active=False)
        monkeypatch.setattr(
            "seopartnerhub.n8n.api.views.process_view_set.N8nWebhookClient",
            lambda *a, **kw: _RecordingWebhook(),
        )

        response = client.post(_trigger_url(process), data={}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert ProcessRun.objects.filter(process=process).count() == 0


class TestProcessRunHistory:
    def test_run_retrieve_returns_run(self, authed_client):
        client, _ = authed_client
        run = ProcessRunFactory()
        response = client.get(_run_detail_url(run))
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(run.id)

    def test_runs_action_returns_history_newest_first(self, authed_client):
        client, _ = authed_client
        process = TelegramProcessFactory()
        older = ProcessRunFactory(
            process=process,
            started_at=timezone.now() - timedelta(minutes=10),
        )
        newer = ProcessRunFactory(process=process, started_at=timezone.now())

        response = client.get(_runs_url(process))
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        results = body.get("results", body) if isinstance(body, dict) else body
        ids = [item["id"] for item in results]
        assert ids[0] == str(newer.id)
        assert str(older.id) in ids


class TestProcessCallback:
    def test_valid_hmac_success_finalizes_run(self, anon_client):
        run = ProcessRunFactory()
        payload = {
            "runId": str(run.id),
            "status": RunStatus.SUCCEEDED.value,
            "result": {"telegram_message_id": 42},
        }
        body = json.dumps(payload).encode("utf-8")
        signature = _sign(body)

        response = anon_client.post(
            _callback_url(),
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE=signature,
        )
        assert response.status_code == status.HTTP_200_OK
        run.refresh_from_db()
        assert run.status == RunStatus.SUCCEEDED.value
        assert run.result_json == {"telegram_message_id": 42}
        assert run.finished_at is not None

    def test_valid_hmac_failure_finalizes_with_error(self, anon_client):
        run = ProcessRunFactory()
        payload = {
            "runId": str(run.id),
            "status": RunStatus.FAILED.value,
            "error": "telegram_unreachable",
        }
        body = json.dumps(payload).encode("utf-8")
        signature = _sign(body)

        response = anon_client.post(
            _callback_url(),
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE=signature,
        )
        assert response.status_code == status.HTTP_200_OK
        run.refresh_from_db()
        assert run.status == RunStatus.FAILED.value
        assert run.error_message == "telegram_unreachable"

    def test_invalid_signature_is_rejected(self, anon_client):
        run = ProcessRunFactory()
        body = json.dumps(
            {"runId": str(run.id), "status": RunStatus.SUCCEEDED.value},
        ).encode("utf-8")

        response = anon_client.post(
            _callback_url(),
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE="bogus",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        run.refresh_from_db()
        assert run.status == RunStatus.RUNNING.value

    def test_unknown_run_is_rejected(self, anon_client):
        body = json.dumps(
            {"runId": str(uuid.uuid4()), "status": RunStatus.SUCCEEDED.value},
        ).encode("utf-8")
        signature = _sign(body)

        response = anon_client.post(
            _callback_url(),
            data=body,
            content_type="application/json",
            HTTP_X_SIGNATURE=signature,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# US4: Sample Telegram-post process
# ---------------------------------------------------------------------------


class TestSampleProcess:
    def test_sample_process_appears_in_list_after_bootstrap(self, authed_client):
        client, _ = authed_client
        SampleProcessBootstrapService.ensure_telegram_sample()

        response = client.get(_list_url())
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        results = body.get("results", body) if isinstance(body, dict) else body
        sample_names = {item["name"] for item in results}
        assert SampleProcessBootstrapService.SAMPLE_NAME in sample_names
