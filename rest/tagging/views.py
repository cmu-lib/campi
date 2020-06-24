from django import forms
from django.db.models import Count, Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from tagging import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


class TagFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="tags with this text in their label", lookup_expr="icontains"
    )


class TagViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Tag.objects.annotate(
        n_images=Count("photograph_tags", distinct=True)
    ).all()
    serializer_class = serializers.TagSerializer
    filterset_class = TagFilter
    ordering = ["label", "n_images"]


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


class PhotographTagViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.PhotographTag.objects.all()
    serializer_class = serializers.PhotographTagPostSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        photograph_tag_serializer = self.get_serializer_class()(data=request.data)
        if photograph_tag_serializer.is_valid():
            obj = photograph_tag_serializer.save()
            obj.user_last_edited = request.user
            obj.save()
            return Response(None, status=status.HTTP_201_CREATED)
        else:
            return Response(
                photograph_tag_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

