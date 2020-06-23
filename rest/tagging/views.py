from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from tagging import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


class TagFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="tags with this text in their label", lookup_expr="icontains"
    )


class TagViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    filterset_class = TagFilter


class TaggingTaskViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.TaggingTask.objects.prefetch_related(
        "assigned_user", "pytorch_model", "tag"
    )
    serializer_class = serializers.TaggingTaskSerializer


class TaggingDecisionViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.TaggingDecision.objects.prefetch_related(
        "photograph",
        "photograph__job",
        "photograph__directory",
        "task",
        "task__assigned_user",
        "task__pytorch_model",
        "task__tag",
    ).all()
    serializer_class = serializers.TaggingDecisionSerializer
