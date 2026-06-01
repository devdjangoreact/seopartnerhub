from __future__ import annotations

from django.urls import path

from seopartnerhub.n8n.api.views.n8n_callback_view import N8nCallbackView

app_name = "n8n"

urlpatterns = [
    path(
        "callbacks/runs/",
        N8nCallbackView.as_view(),
        name="callback-runs",
    ),
]
