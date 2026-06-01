from __future__ import annotations

from django.urls import path

from seopartnerhub.fake_db.api.views import FakeDbManifestView
from seopartnerhub.fake_db.api.views import FakeDbSectionView

app_name = "fake_db"

urlpatterns = [
    path("manifest/", FakeDbManifestView.as_view(), name="manifest"),
    path("<str:group>/<str:section>/", FakeDbSectionView.as_view(), name="section"),
]
