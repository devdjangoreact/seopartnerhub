from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class N8nConfig(AppConfig):
    name = "seopartnerhub.n8n"
    label = "n8n"
    verbose_name = _("n8n Processes")
    default_auto_field = "django.db.models.BigAutoField"
