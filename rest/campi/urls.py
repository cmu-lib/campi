from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
import photograph.views
import collection.views
import campi.views
import cv.views
import tagging.views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r"photograph", photograph.views.PhotographViewSet)
router.register(r"directory", collection.views.DirectoryViewSet)
router.register(r"job", collection.views.JobViewSet)
router.register(r"pytorch_model", cv.views.PytorchModelViewset)
router.register(r"close_match/run", cv.views.CloseMatchRunViewset)
router.register(r"close_match/set", cv.views.CloseMatchSetViewset)
router.register(r"close_match/set_membership", cv.views.CloseMatchSetMembershipViewset)
router.register(r"tagging/tag", tagging.views.TagViewset)
router.register(r"tagging/task", tagging.views.TaggingTaskViewset)
router.register(r"tagging/decision", tagging.views.TaggingDecisionViewset)
router.register(r"tagging/photograph_tag", tagging.views.PhotographTagViewset)
router.register(r"gcv/face_annotation", photograph.views.FaceAnnotationViewset)
router.register(r"gcv/object_annotation", photograph.views.ObjectAnnotationViewset)
router.register(
    r"gcv/object_annotation_labels", photograph.views.ObjectAnnotationLabelViewset
)
router.register(
    r"gcv/object_annotation_labels_paginated",
    photograph.views.PaginatedObjectAnnotationLabelViewset,
)
router.register(r"gcv/photo_labels", photograph.views.PhotoLabelViewset)

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
