from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
import photograph.views
import collection.views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r"photograph", photograph.views.PhotographViewSet)
router.register(r"directory", collection.views.DirectoryViewSet)


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
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(
        r"^api/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]
