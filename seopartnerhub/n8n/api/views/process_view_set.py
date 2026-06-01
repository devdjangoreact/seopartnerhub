from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from seopartnerhub.n8n.api.serializers.process_detail_serializer import (
    ProcessDetailSerializer,
)
from seopartnerhub.n8n.api.serializers.process_list_serializer import (
    ProcessListSerializer,
)
from seopartnerhub.n8n.api.serializers.process_run_serializer import (
    ProcessRunSerializer,
)
from seopartnerhub.n8n.api.serializers.process_update_serializer import (
    ProcessUpdateSerializer,
)
from seopartnerhub.n8n.integrations.n8n_webhook_client import N8nWebhookClient
from seopartnerhub.n8n.selectors.process_run_selector import ProcessRunSelector
from seopartnerhub.n8n.selectors.process_selector import ProcessSelector
from seopartnerhub.n8n.services.process_configuration_service import (
    ProcessConfigurationService,
)
from seopartnerhub.n8n.services.process_trigger_service import ProcessNotActiveError
from seopartnerhub.n8n.services.process_trigger_service import ProcessTriggerService

if TYPE_CHECKING:
    from rest_framework.request import Request

    from seopartnerhub.n8n.integrations.webhook_trigger import WebhookTrigger

logger = logging.getLogger(__name__)


class ProcessViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """List, retrieve, partial-update, trigger, and history actions for processes."""

    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "patch", "post", "head", "options")
    lookup_value_regex = r"\d+"

    def get_queryset(self):
        return ProcessSelector.all_with_latest_run()

    def get_serializer_class(self):
        if self.action == "list":
            return ProcessListSerializer
        if self.action in {"partial_update", "update"}:
            return ProcessUpdateSerializer
        if self.action == "runs":
            return ProcessRunSerializer
        return ProcessDetailSerializer

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        process = self.get_object()
        serializer = ProcessUpdateSerializer(
            process,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        updated = ProcessConfigurationService.apply_partial_update(
            process=process,
            validated=serializer.validated_data,
        )
        return Response(ProcessDetailSerializer(updated).data)

    def update(self, request: Request, *args, **kwargs) -> Response:
        kwargs["partial"] = True
        return self.partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="trigger")
    def trigger(self, request: Request, pk: str | None = None) -> Response:
        process = self.get_object()
        service = self._build_trigger_service()
        try:
            run = service.trigger_manual(process=process, user=request.user)
        except ProcessNotActiveError as exc:
            msg = "Process is not active."
            raise PermissionDenied(msg) from exc
        return Response(
            ProcessRunSerializer(run).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="runs")
    def runs(self, request: Request, pk: str | None = None) -> Response:
        process = self.get_object()
        queryset = ProcessRunSelector.for_process(process.pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProcessRunSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProcessRunSerializer(queryset, many=True)
        return Response(serializer.data)

    def _build_trigger_service(self) -> ProcessTriggerService:
        injected = getattr(self, "_webhook_trigger", None)
        webhook: WebhookTrigger = injected or N8nWebhookClient()
        return ProcessTriggerService(webhook_trigger=webhook)
