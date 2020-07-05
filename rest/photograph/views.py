from django.db.models import Count, Prefetch, OuterRef
from django.db.models.functions import Extract
from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from photograph import serializers, models
import collection
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
import tagging.models


class PhotographFilter(filters.FilterSet):
    directory = filters.ModelMultipleChoiceFilter(
        queryset=collection.models.Directory.objects.all()
    )
    all_directories = filters.ModelChoiceFilter(
        queryset=collection.models.Directory.objects.all()
    )
    date_taken_early = filters.DateFromToRangeFilter()
    date_taken_late = filters.DateFromToRangeFilter()
    digitized_date = filters.DateFromToRangeFilter()
    job = filters.ModelChoiceFilter(queryset=collection.models.Job.objects.all())
    job_tag = filters.ModelChoiceFilter(
        queryset=collection.models.JobTag.objects.all(), field_name="job__tags"
    )
    tag = filters.ModelChoiceFilter(
        queryset=tagging.models.Tag.objects.all(), field_name="photograph_tags__tag"
    )
    image_path = filters.CharFilter(lookup_expr="icontains")


def prepare_photograph_qs(qs):
    ordered_tags = tagging.models.PhotographTag.objects.select_related(
        "tag", "user_last_modified"
    ).order_by("-last_updated")
    qs = (
        qs.select_related("directory", "job")
        .prefetch_related(
            "job__tags", Prefetch("photograph_tags", queryset=ordered_tags)
        )
        .all()
    )
    return qs


class PhotographViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = prepare_photograph_qs(models.Photograph.objects.all())
    ordered_tags = tagging.models.PhotographTag.objects.select_related(
        "tag", "user_last_modified"
    ).order_by("-last_updated")
    queryset = (
        models.Photograph.objects.select_related("directory", "job")
        .prefetch_related(
            "job__tags", Prefetch("photograph_tags", queryset=ordered_tags)
        )
        .all()
    )
    ordering_fields = ["date_taken_early", "date_taken_late", "digitized_date"]
    filterset_class = PhotographFilter
    serializer_class = serializers.PhotographDetailSerializer
    serializer_action_classes = {
        "list": serializers.PhotographListSerializer,
        "detail": serializers.PhotographDetailSerializer,
    }
    queryset_action_classes = {"list": queryset, "detail": queryset}

    @action(detail=False, methods=["get"], name="Get range of years")
    def digitized_date_range(self, request):
        years_array = (
            self.filterset_class(request.GET, queryset=self.get_queryset())
            .qs.annotate(year=Extract("digitized_date", "year"))
            .values("year")
            .order_by("year")
            .annotate(n=Count("year"))
        )
        return Response(years_array)


class FaceAnnotationFilter(filters.FilterSet):
    photograph = filters.ModelChoiceFilter(queryset=models.Photograph.objects.all())
    detection_confidence = filters.RangeFilter()


class FaceAnnotationViewset(viewsets.ModelViewSet):
    queryset = models.FaceAnnotation.objects.prefetch_related(
        Prefetch("photograph", prepare_photograph_qs(models.Photograph.objects.all()))
    ).all()
    filterset_class = FaceAnnotationFilter
    serializer_class = serializers.FaceAnnotationSerializer
    ordering_fields = [
        "photograph",
        "detection_confidence",
        "joy_likelihood",
        "sorrow_likelihood",
        "anger_likelihood",
        "surprise_likelihood",
        "under_exposed_likelihood",
        "blurred_likelihood",
        "headwear_likelihood",
    ]


class ObjectAnnotationFilter(filters.FilterSet):
    photograph = filters.ModelChoiceFilter(queryset=models.Photograph.objects.all())
    score = filters.RangeFilter()
    label = filters.CharFilter(field_name="label__label", lookup_expr="icontains")


class ObjectAnnotationViewset(viewsets.ModelViewSet):
    queryset = (
        models.ObjectAnnotation.objects.select_related("label")
        .prefetch_related(
            Prefetch(
                "photograph", prepare_photograph_qs(models.Photograph.objects.all())
            )
        )
        .all()
    )
    filterset_class = ObjectAnnotationFilter
    serializer_class = serializers.ObjectAnnotationSerializer
    ordering_fields = ["photograph", "score", "photograph__date_taken_early"]


class ObjectAnnotationLabelViewset(viewsets.ModelViewSet):
    queryset = models.ObjectAnnotationLabel.objects.order_by("label").annotate(
        n_annotations=Count("annotations", distinct=True)
    )
    serializer_class = serializers.ObjectAnnotationLabelSerializer
    pagination_class = None

