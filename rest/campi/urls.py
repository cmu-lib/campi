from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
import photograph.views
import collection.views
import campi.views
import cv.views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r"photograph", photograph.views.PhotographViewSet)
router.register(r"directory", collection.views.DirectoryViewSet)
router.register(r"job", collection.views.JobViewSet)
router.register(r"job_tag", collection.views.JobTagViewSet)
router.register(r"pytorch_model", cv.views.PytorchModelViewset)
router.register(r"annoy_idx", cv.views.AnnoyIdxViewset)
router.register(r"close_match/run", cv.views.CloseMatchRunViewset)
router.register(r"close_match/set", cv.views.CloseMatchSetViewset)

schema_view = get_schema_view(
    openapi.Info(
        title="CAMPI API",
        default_version="v1",
        description="API for teh Computaitonal Metadata for Photo Archvies Initiative at Carnegie Mellon University Libraries",
        contact=openapi.Contact(email="mlincoln@andrew.cmu.edu"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/current_user/", campi.views.CurrentUserView.as_view(), name="current_user"
    ),
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/admin/", admin.site.urls),
    path("api/accounts/", include("django.contrib.auth.urls")),
    re_path(
        r"^api/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("api/silk/", include("silk.urls", namespace="silk")),
]
