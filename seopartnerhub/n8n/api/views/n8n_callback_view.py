from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from seopartnerhub.n8n.api.serializers.process_run_serializer import (
    ProcessRunSerializer,
)
from seopartnerhub.n8n.services.process_run_callback_service import CallbackAuthError
from seopartnerhub.n8n.services.process_run_callback_service import CallbackPayloadError
from seopartnerhub.n8n.services.process_run_callback_service import (
    ProcessRunCallbackService,
)
from seopartnerhub.n8n.services.process_run_callback_service import (
    TerminalRunConflictError,
)
from seopartnerhub.n8n.services.process_run_callback_service import UnknownRunError

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)


class N8nCallbackView(APIView):
    """HMAC-authenticated callback endpoint for n8n run completion."""

    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request: Request) -> Response:
        raw_body = request.body
        signature = request.META.get("HTTP_X_SIGNATURE")
        try:
            ProcessRunCallbackService.verify_signature(
                raw_body=raw_body,
                signature=signature,
            )
            payload = ProcessRunCallbackService.parse_payload(raw_body)
            run = ProcessRunCallbackService.apply_callback(payload=payload)
        except CallbackAuthError:
            return Response(
                {
                    "error": {
                        "code": "invalid_signature",
                        "message": "Invalid signature.",
                    },
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except UnknownRunError:
            return Response(
                {"error": {"code": "unknown_run", "message": "Unknown run id."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except TerminalRunConflictError:
            return Response(
                {
                    "error": {
                        "code": "terminal_run_conflict",
                        "message": "Run is already in a terminal state.",
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )
        except CallbackPayloadError as exc:
            return Response(
                {"error": {"code": str(exc), "message": "Invalid callback payload."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ProcessRunSerializer(run).data, status=status.HTTP_200_OK)
