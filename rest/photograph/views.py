from django import forms
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db.models.functions import Extract
from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from photograph import serializers, models
import collection
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


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

    class Meta:
        model = models.Photograph
        fields = [
            "directory",
            "job",
            "all_directories",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
        ]


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
