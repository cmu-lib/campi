from django import forms
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from rest_framework import viewsets
from collection import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


class DirectoryFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="Directories containing this text in their label",
        lookup_expr="icontains",
    )

    digitized_date = filters.DateFromToRangeFilter(
        field_name="immediate_photographs__digitized_date", distinct=True
    )

    def is_top(self, queryset, name, value):
        if value == "true":
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
