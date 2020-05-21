from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from collection import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


class DirectoryFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="Directories containing this text in their label",
        lookup_expr="icontains",
    )


class DirectoryViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Directory.objects.select_related("parent_directory").all()
    serializer_class = serializers.DirectoryDetailSerializer
    serializer_action_classes = {"list": serializers.DirectoryListSerializer}
    filterset_class = DirectoryFilter
    ordering_fields = ["label"]
    queryset_action_classes = {
        "list": queryset,
        "detail": queryset.prefetch_related("child_directories"),
    }
