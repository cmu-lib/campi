from django.db.models import (
    Count,
    Prefetch,
    OuterRef,
    Exists,
    ExpressionWrapper,
    BooleanField,
    F,
)
from django.db.models.functions import Extract
from django.contrib.postgres.search import SearchRank, SearchQuery
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from photograph import serializers, models
import collection
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
import tagging.models
from cv.models import CloseMatchSetMembership


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
    tag = filters.ModelChoiceFilter(
        queryset=tagging.models.Tag.objects.all(), field_name="photograph_tags__tag"
    )
    image_path = filters.CharFilter(lookup_expr="icontains")
    gcv_object = filters.ModelChoiceFilter(
        queryset=models.ObjectAnnotationLabel.objects.all(),
        field_name="objectannotation__label",
    )
    gcv_label = filters.ModelChoiceFilter(
        queryset=models.PhotoLabel.objects.all(), field_name="label_annotations__label"
    )
    in_close_match_set = filters.BooleanFilter(field_name="in_close_match_set")
    image_text = filters.CharFilter(method="get_text")

    def get_text(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return (
                queryset.annotate(
                    rank=SearchRank(F("image_search_text"), SearchQuery(value))
                )
                .filter(rank__gt=0)
                .order_by("-rank")
            )


def prepare_photograph_qs(qs):
    ordered_tags = tagging.models.PhotographTag.objects.select_related(
        "tag", "user_last_modified"
    ).order_by("-last_updated")
    ordered_decisions = tagging.models.TaggingDecision.objects.order_by("-created_on")
    ordered_labels = models.PhotoLabelAnnotation.objects.select_related(
        "label"
    ).order_by("-score")
    qs = (
        qs.select_related("directory", "job")
        .annotate(
            in_close_match_set=Exists(
                CloseMatchSetMembership.objects.filter(
                    state=CloseMatchSetMembership.ACCEPTED, photograph=OuterRef("pk"),
                )
            )
        )
        .prefetch_related(
            Prefetch("photograph_tags", queryset=ordered_tags),
            Prefetch("decisions", queryset=ordered_decisions),
            Prefetch("label_annotations", queryset=ordered_labels),
        )
        .distinct()
    )
    return qs


def prepare_photograph_detail_qs(qs):
    object_annotations = models.ObjectAnnotation.objects.select_related("label").all()
    ordered_tags = tagging.models.PhotographTag.objects.select_related(
        "tag", "user_last_modified"
    ).order_by("-last_updated")
    ordered_decisions = tagging.models.TaggingDecision.objects.order_by("-created_on")
    ordered_labels = models.PhotoLabelAnnotation.objects.select_related(
        "label"
    ).order_by("-score")
    ordered_text_annotations = models.TextAnnotation.objects.order_by("sequence")
    qs = (
        qs.select_related("directory", "job")
        .annotate(
            in_close_match_set=Exists(
                CloseMatchSetMembership.objects.filter(
                    state=CloseMatchSetMembership.ACCEPTED, photograph=OuterRef("pk")
                )
            )
        )
        .prefetch_related(
            Prefetch("photograph_tags", queryset=ordered_tags),
            Prefetch("decisions", queryset=ordered_decisions),
            Prefetch("objectannotation", queryset=object_annotations),
            Prefetch("label_annotations", queryset=ordered_labels),
            "faceannotation",
            Prefetch("textannotation", queryset=ordered_text_annotations),
        )
        .distinct()
    )
    return qs


class PhotographViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = prepare_photograph_qs(models.Photograph.objects.all())
    ordering_fields = ["date_taken_early", "date_taken_late", "digitized_date"]
    filterset_class = PhotographFilter
    serializer_class = serializers.PhotographDetailSerializer
    serializer_action_classes = {
        "list": serializers.PhotographListSerializer,
        "retrieve": serializers.PhotographDetailSerializer,
    }
    queryset_action_classes = {
        "list": queryset,
        "retrieve": prepare_photograph_detail_qs(models.Photograph.objects.all()),
    }

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
    joy_likelihood = filters.NumberFilter(lookup_expr="gte")
    sorrow_likelihood = filters.NumberFilter(lookup_expr="gte")
    anger_likelihood = filters.NumberFilter(lookup_expr="gte")
    surprise_likelihood = filters.NumberFilter(lookup_expr="gte")
    headwear_likelihood = filters.NumberFilter(lookup_expr="gte")


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
        n_annotations=Count("annotations", distinct=True),
        n_images=Count("annotations__photograph", distinct=True),
    )
    serializer_class = serializers.ObjectAnnotationLabelSerializer
    ordering_fields = ["label", "n_annotations", "n_images"]
    pagination_class = None


class ObjectAnnotationLabelFilter(filters.FilterSet):
    label = filters.CharFilter(field_name="label", lookup_expr="icontains")
    job = filters.ModelChoiceFilter(
        queryset=collection.models.Job.objects.all(), method="by_job"
    )

    def by_job(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    collection.models.Job.objects.filter(
                        id=value.id, photographs__objectannotation__label=OuterRef("pk")
                    )
                )
            )

    directory = filters.ModelChoiceFilter(
        queryset=collection.models.Directory.objects.all(), method="by_directory"
    )

    def by_directory(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    collection.models.Directory.objects.filter(
                        id=value.id,
                        immediate_photographs__objectannotation__label=OuterRef("pk"),
                    )
                )
            )

    tag = filters.ModelChoiceFilter(
        queryset=tagging.models.Tag.objects.all(), method="by_tag"
    )

    def by_tag(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    tagging.models.Tag.objects.filter(
                        id=value.id,
                        photograph_tags__photograph__objectannotation__label=OuterRef(
                            "pk"
                        ),
                    )
                )
            )

    gcv_label = filters.ModelChoiceFilter(
        queryset=models.PhotoLabel.objects.all(), method="by_gcv_label"
    )

    def by_gcv_label(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    models.PhotoLabel.objects.filter(
                        id=value.id,
                        annotations__photograph__objectannotation__label=OuterRef("pk"),
                    )
                )
            )


class PaginatedObjectAnnotationLabelViewset(ObjectAnnotationLabelViewset):
    filterset_class = ObjectAnnotationLabelFilter
    pagination_class = LimitOffsetPagination


class PhotoLabelFilter(filters.FilterSet):
    label = filters.CharFilter(field_name="label", lookup_expr="icontains")
    gcv_object = filters.ModelChoiceFilter(
        queryset=models.ObjectAnnotationLabel.objects.all(), method="by_gcv_object"
    )

    def by_job(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    collection.models.Job.objects.filter(
                        id=value.id,
                        photographs__label_annotations__label=OuterRef("pk"),
                    )
                )
            )

    directory = filters.ModelChoiceFilter(
        queryset=collection.models.Directory.objects.all(), method="by_directory"
    )

    def by_directory(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    collection.models.Directory.objects.filter(
                        id=value.id,
                        immediate_photographs__label_annotations__label=OuterRef("pk"),
                    )
                )
            )

    tag = filters.ModelChoiceFilter(
        queryset=tagging.models.Tag.objects.all(), method="by_tag"
    )

    def by_tag(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    tagging.models.Tag.objects.filter(
                        id=value.id,
                        photograph_tags__photograph__label_annotations__label=OuterRef(
                            "pk"
                        ),
                    )
                )
            )

    gcv_object = filters.ModelChoiceFilter(
        queryset=models.ObjectAnnotationLabel.objects.all(), method="by_gcv_object"
    )

    def by_gcv_object(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    models.ObjectAnnotationLabel.objects.filter(
                        id=value.id,
                        annotations__photograph__label_annotations__label=OuterRef(
                            "pk"
                        ),
                    )
                )
            )


class PhotoLabelViewset(viewsets.ModelViewSet):
    queryset = models.PhotoLabel.objects.annotate(
        n_images=Count("annotations__photograph", distinct=True)
    ).all()
    filterset_class = PhotoLabelFilter
    serializer_class = serializers.PhotoLabelSerializer
    ordering_fields = ["label", "n_images"]

