from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from photograph import views as photograph_views
from collection import views as collection_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r"photograph", photograph_views.PhotographViewSet)
router.register(r"collection", collection_views.CollectionViewSet)


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
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
