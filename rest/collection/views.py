from django import forms
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, BooleanField, ExpressionWrapper
from rest_framework import viewsets
from collection import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


class DirectoryFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="Directories containing this text in their label",
        lookup_expr="icontains",
    )

    # digitized_date = filters.DateFromToRangeFilter(
    #     field_name="immediate_photographs__digitized_date", distinct=True
    # )

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
    label = filters.CharFilter(
        help_text="Jobs containing this text in their label", lookup_expr="icontains"
    )


class JobViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Job.objects.annotate(n_images=Count("photographs", distinct=True))
    serializer_class = serializers.JobListSerializer
    serializer_action_classes = {"list": serializers.JobListSerializer}
    filterset_class = JobFilter
    ordering_fields = ["job_code", "label", "date_start", "date_end"]
    queryset_action_classes = {"list": queryset, "detail": queryset}
