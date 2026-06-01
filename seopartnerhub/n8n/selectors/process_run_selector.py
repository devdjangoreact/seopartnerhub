from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils import timezone

from seopartnerhub.n8n.models import ProcessRun
from seopartnerhub.n8n.models import RunStatus

if TYPE_CHECKING:
    from datetime import datetime
    from datetime import timedelta
    from uuid import UUID

    from django.db.models import QuerySet


class ProcessRunSelector:
    """Read-only queries for :class:`ProcessRun`."""

    @staticmethod
    def get_by_id(run_id: UUID) -> ProcessRun | None:
        return ProcessRun.objects.filter(pk=run_id).first()

    @staticmethod
    def for_process(process_id: int) -> QuerySet[ProcessRun]:
        return ProcessRun.objects.filter(process_id=process_id).order_by("-started_at")

    @staticmethod
    def running_started_before(threshold: datetime) -> QuerySet[ProcessRun]:
        return ProcessRun.objects.filter(
            status=RunStatus.RUNNING.value,
            started_at__lt=threshold,
        )

    @staticmethod
    def running_older_than(age: timedelta) -> QuerySet[ProcessRun]:
        cutoff = timezone.now() - age
        return ProcessRunSelector.running_started_before(cutoff)
