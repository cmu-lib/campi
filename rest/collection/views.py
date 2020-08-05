from django.db import transaction
from django.db.models import Count, Q, BooleanField, ExpressionWrapper, Exists, OuterRef
from rest_framework import viewsets, status
from rest_framework.decorators import action
from collection import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
import tagging.models
import photograph.models


class DirectoryFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="Directories containing this text in their label",
        lookup_expr="icontains",
    )
    job = filters.ModelChoiceFilter(queryset=models.Job.objects.all(), method="by_job")

    def by_job(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    models.Job.objects.filter(
                        id=value.id, photographs__directory=OuterRef("pk")
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
                        photograph_tags__photograph__directory=OuterRef("pk"),
                    )
                )
            )

    gcv_object = filters.ModelChoiceFilter(
        queryset=photograph.models.ObjectAnnotationLabel.objects.all(),
        method="by_gcv_object",
    )

    def by_gcv_object(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    photograph.models.ObjectAnnotationLabel.objects.filter(
                        id=value.id, annotations__photograph__directory=OuterRef("pk")
                    )
                )
            )

    gcv_label = filters.ModelChoiceFilter(
        queryset=photograph.models.PhotoLabel.objects.all(), method="by_gcv_label"
    )

    def by_gcv_label(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    photograph.models.PhotoLabel.objects.filter(
                        id=value.id, annotations__photograph__directory=OuterRef("pk")
                    )
                )
            )

    is_top = filters.BooleanFilter(method="filter_is_top")

    def filter_is_top(self, queryset, name, value):
        if value:
            return queryset.filter(parent_directory__isnull=True)
        else:
            return queryset


class DirectoryViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Directory.objects.annotate(
        n_images=Count("immediate_photographs", distinct=True)
    ).select_related("parent_directory")
    serializer_class = serializers.DirectoryDetailSerializer
    serializer_action_classes = {"list": serializers.DirectoryListSerializer}
    filterset_class = DirectoryFilter
    ordering_fields = ["label"]
    queryset_action_classes = {
        "list": queryset,
        "detail": queryset.prefetch_related("child_directories"),
    }
    pagination_class = None

    def get_queryset(self):
        qs = self.queryset
        if "digitized_date_before" in self.request.GET:
            qs = qs.annotate(
                n_images=Count(
                    "immediate_photographs",
                    distinct=True,
                    filter=Q(
                        immediate_photographs__digitized_date__lt=self.request.GET[
                            "digitized_date_before"
                        ]
                    ),
                )
            )
        if "digitized_date_after" in self.request.GET:
            qs = qs.annotate(
                n_images=Count(
                    "immediate_photographs",
                    distinct=True,
                    filter=Q(
                        immediate_photographs__digitized_date__gt=self.request.GET[
                            "digitized_date_after"
                        ]
                    ),
                )
            )

        return qs


class JobFilter(filters.FilterSet):
    text = filters.CharFilter(
        help_text="Jobs containing this text in their label or job ID number",
        method="search_text",
    )

    def search_text(self, queryset, name, value):
        if value != "":
            return queryset.filter(
                Q(label__icontains=value) | Q(job_code__icontains=value)
            )
        else:
            return queryset

    directory = filters.ModelChoiceFilter(
        queryset=models.Directory.objects.all(), method="by_directory"
    )

    def by_directory(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    models.Directory.objects.filter(
                        id=value.id, immediate_photographs__job=OuterRef("pk")
                    )
                )
            )

    tag = filters.ModelChoiceFilter(
        queryset=tagging.models.Tag.objects.all(),
        field_name="photographs__photograph_tags__tag",
    )

    def by_tag(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    tagging.models.Tag.objects.filter(
                        id=value.id, photograph_tags__photograph__job=OuterRef("pk")
                    )
                )
            )

    gcv_object = filters.ModelChoiceFilter(
        queryset=photograph.models.ObjectAnnotationLabel.objects.all(),
        method="by_gcv_object",
    )

    def by_gcv_object(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    photograph.models.ObjectAnnotationLabel.objects.filter(
                        id=value.id, annotations__photograph__job=OuterRef("pk")
                    )
                )
            )

    gcv_label = filters.ModelChoiceFilter(
        queryset=photograph.models.PhotoLabel.objects.all(), method="by_gcv_label"
    )

    def by_gcv_label(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    photograph.models.PhotoLabel.objects.filter(
                        id=value.id, annotations__photograph__job=OuterRef("pk")
                    )
                )
            )


class JobViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Job.objects.annotate(n_images=Count("photographs", distinct=True))
    serializer_class = serializers.JobListSerializer
    serializer_action_classes = {
        "list": serializers.JobListSerializer,
        "detail": serializers.JobDetailSerializer,
    }
    filterset_class = JobFilter
    ordering_fields = ["job_code", "label", "date_start", "date_end", "n_images"]
    queryset_action_classes = {
        "list": queryset,
        "detail": queryset.prefetch_related("tags"),
    }
