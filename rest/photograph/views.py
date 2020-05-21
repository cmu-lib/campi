from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from photograph import serializers, models
import collection
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


class PhotographFilter(filters.FilterSet):
    directory = filters.ModelChoiceFilter(
        queryset=collection.models.Directory.objects.all()
    )
    all_directories = filters.ModelChoiceFilter(
        queryset=collection.models.Directory.objects.all()
    )
    date_taken_early = filters.DateFromToRangeFilter()
    date_taken_late = filters.DateFromToRangeFilter()

    class Meta:
        model = models.Photograph
        fields = ["directory", "all_directories", "date_taken_early", "date_taken_late"]


class PhotographViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Photograph.objects.select_related("directory").all()
    ordering_fields = ["date_taken_early", "date_taken_late", "digitized_date"]
    filterset_class = PhotographFilter
    serializer_class = serializers.PhotographDetailSerializer
    serializer_action_classes = {
        "list": serializers.PhotographListSerializer,
        "detail": serializers.PhotographDetailSerializer,
    }
    queryset_action_classes = {"list": queryset, "detail": queryset}
