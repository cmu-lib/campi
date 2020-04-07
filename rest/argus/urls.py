from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from photograph import views as photograph_views
from collection import views as collection_views

router = routers.DefaultRouter()
router.register(r"photograph", photograph_views.PhotographViewSet)
router.register(r"collection", collection_views.CollectionViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
]
