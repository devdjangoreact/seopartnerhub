from __future__ import annotations

import logging
from pathlib import Path

from django.apps import apps
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from seopartnerhub.fake_db.services.fake_db_section_loader import FakeDbSectionLoader

logger = logging.getLogger(__name__)

_STUB_TAG = "fake-db (stub)"


def _build_loader() -> FakeDbSectionLoader:
    app_config = apps.get_app_config("fake_db")
    data_dir = Path(app_config.path) / "data"
    return FakeDbSectionLoader(data_dir=data_dir)


_loader: FakeDbSectionLoader | None = None


def _get_loader() -> FakeDbSectionLoader:
    global _loader  # noqa: PLW0603
    if _loader is None:
        _loader = _build_loader()
    return _loader


class FakeDbManifestView(APIView):
    """STUB. List every fake-db section grouped by `apps/` and `pages/`."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=[_STUB_TAG],
        summary="STUB: list available fake-db sections",
        responses={200: OpenApiResponse(description="Mapping of group -> sections.")},
    )
    def get(self, request: Request) -> Response:  # noqa: ARG002
        return Response(_get_loader().manifest())


class FakeDbSectionView(APIView):
    """STUB. Return the JSON fixture for ``<group>/<section>.json``."""

    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=[_STUB_TAG],
        summary="STUB: read a single fake-db section",
        parameters=[
            OpenApiParameter(
                name="group",
                location=OpenApiParameter.PATH,
                type=str,
                enum=["apps", "pages"],
                description="Top-level group from frontend/full-version/src/fake-db-json/.",
            ),
            OpenApiParameter(
                name="section",
                location=OpenApiParameter.PATH,
                type=str,
                description="JSON filename without extension (e.g. `userProfile`).",
            ),
        ],
        responses={
            200: OpenApiResponse(description="Raw JSON fixture payload."),
            404: OpenApiResponse(description="Unknown group or section."),
        },
    )
    def get(self, request: Request, group: str, section: str) -> Response:  # noqa: ARG002
        try:
            payload = _get_loader().load(group=group, section=section)
        except FileNotFoundError:
            logger.warning(
                "fake_db_section_missing",
                extra={"group": group, "section": section},
            )
            return Response(
                {"error": {"code": "not_found", "message": "fake-db section not found"}},
                status=404,
            )
        except ValueError:
            logger.warning(
                "fake_db_section_invalid",
                extra={"group": group, "section": section},
            )
            return Response(
                {"error": {"code": "invalid", "message": "invalid fake-db section path"}},
                status=404,
            )
        return Response(payload)
