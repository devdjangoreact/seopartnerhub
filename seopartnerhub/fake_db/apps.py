from __future__ import annotations

from django.apps import AppConfig


class FakeDbConfig(AppConfig):
    """STUB DATA — serves mock fixtures mirrored from
    ``frontend/full-version/src/fake-db-json/`` for any starter-kit view that
    does not yet have a real Django domain endpoint.

    Replace usages with real endpoints when the domain is implemented.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "seopartnerhub.fake_db"
    verbose_name = "Fake DB (stub fixtures)"
