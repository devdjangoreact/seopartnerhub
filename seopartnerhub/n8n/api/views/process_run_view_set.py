from __future__ import annotations

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from seopartnerhub.n8n.api.serializers.process_run_serializer import (
    ProcessRunSerializer,
)
from seopartnerhub.n8n.models import ProcessRun


class ProcessRunViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Retrieve a single :class:`ProcessRun` by id."""

    permission_classes = (IsAuthenticated,)
    serializer_class = ProcessRunSerializer
    queryset = ProcessRun.objects.all()
    lookup_field = "pk"
