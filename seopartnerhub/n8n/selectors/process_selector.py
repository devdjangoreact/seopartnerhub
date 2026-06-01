from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import OuterRef
from django.db.models import Subquery

from seopartnerhub.n8n.models import Process
from seopartnerhub.n8n.models import ProcessRun

if TYPE_CHECKING:
    from django.db.models import QuerySet


class ProcessSelector:
    """Read-only queries for :class:`Process`."""

    @staticmethod
    def all_with_latest_run() -> QuerySet[Process]:
        latest_run_qs = ProcessRun.objects.filter(process=OuterRef("pk")).order_by(
            "-started_at",
        )
        return Process.objects.annotate(
            latest_run_id=Subquery(latest_run_qs.values("id")[:1]),
            latest_run_status=Subquery(latest_run_qs.values("status")[:1]),
            latest_run_started_at=Subquery(latest_run_qs.values("started_at")[:1]),
            latest_run_finished_at=Subquery(latest_run_qs.values("finished_at")[:1]),
        )

    @staticmethod
    def get_by_id(process_id: int) -> Process | None:
        return Process.objects.filter(pk=process_id).first()

    @staticmethod
    def active_with_schedule() -> QuerySet[Process]:
        return Process.objects.filter(is_active=True).exclude(schedule_cron="")
