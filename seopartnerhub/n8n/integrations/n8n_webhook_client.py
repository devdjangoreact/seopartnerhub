from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import httpx
from django.conf import settings

from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTrigger
from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTriggerError

if TYPE_CHECKING:
    from seopartnerhub.n8n.schemas.json_value import JsonObject

logger = logging.getLogger(__name__)

HTTP_BAD_REQUEST_THRESHOLD = 400


class N8nWebhookClient(WebhookTrigger):
    """HTTPX-based :class:`WebhookTrigger` for the n8n webhook surface."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url or settings.N8N_WEBHOOK_BASE_URL
        self._timeout = (
            timeout_seconds
            if timeout_seconds is not None
            else float(settings.N8N_REQUEST_TIMEOUT_SECONDS)
        )
        self._client = client

    def trigger(self, *, webhook_path: str, payload: JsonObject) -> JsonObject:
        url = self._resolve_url(webhook_path)
        logger.info(
            "n8n_webhook_trigger_send",
            extra={"url": url, "run_id": payload.get("run_id")},
        )
        try:
            response = self._post(url, payload)
        except httpx.HTTPError as exc:
            logger.exception(
                "n8n_webhook_trigger_transport_failed",
                extra={"url": url},
            )
            msg = "n8n_transport_failed"
            raise WebhookTriggerError(msg) from exc

        if response.status_code >= HTTP_BAD_REQUEST_THRESHOLD:
            logger.error(
                "n8n_webhook_trigger_status_failed",
                extra={"url": url, "status": response.status_code},
            )
            msg = "n8n_status_failed"
            raise WebhookTriggerError(msg)

        return self._parse_response(response)

    def _resolve_url(self, webhook_path: str) -> str:
        if webhook_path.startswith(("http://", "https://")):
            return webhook_path
        base = self._base_url.rstrip("/") + "/"
        return urljoin(base, webhook_path.lstrip("/"))

    def _post(self, url: str, payload: JsonObject) -> httpx.Response:
        if self._client is not None:
            return self._client.post(url, json=payload, timeout=self._timeout)
        with httpx.Client(timeout=self._timeout) as client:
            return client.post(url, json=payload)

    @staticmethod
    def _parse_response(response: httpx.Response) -> JsonObject:
        if not response.content:
            return {}
        try:
            data = response.json()
        except ValueError:
            return {"raw": response.text}
        if isinstance(data, dict):
            return data
        return {"data": data}
