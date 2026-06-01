from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from seopartnerhub.n8n.api.views import ProcessRunViewSet
from seopartnerhub.n8n.api.views import ProcessViewSet
from seopartnerhub.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("n8n/processes", ProcessViewSet, basename="n8n-process")
router.register("n8n/runs", ProcessRunViewSet, basename="n8n-run")


app_name = "api"
urlpatterns = router.urls
