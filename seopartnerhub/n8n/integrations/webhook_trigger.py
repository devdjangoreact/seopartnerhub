from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:
    from seopartnerhub.n8n.schemas.json_value import JsonObject


class WebhookTriggerError(Exception):
    """Raised when triggering an n8n webhook fails."""


class WebhookTrigger(Protocol):
    """Outbound n8n webhook trigger abstraction.

    Concrete adapters (HTTPX, fakes for tests) implement this protocol.
    """

    def trigger(self, *, webhook_path: str, payload: JsonObject) -> JsonObject:
        """Send ``payload`` to the n8n webhook resolved from ``webhook_path``.

        Returns the JSON response body parsed as a JSON object. May raise
        :class:`WebhookTriggerError` on transport, timeout, or non-2xx
        responses.
        """
