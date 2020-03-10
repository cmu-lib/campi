from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from photograph import views as photograph_views

router = routers.DefaultRouter()
router.register(r"photograph", photograph_views.PhotographViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls", namespace="rest_framework")),
]
