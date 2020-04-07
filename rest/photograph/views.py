from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from photograph import serializers, models
from collection import models as collection_models
from django_filters import rest_framework as filters
from argus.views import GetSerializerClassMixin


class PhotographFilter(filters.FilterSet):
    collection = filters.ModelChoiceFilter(
        queryset=collection_models.Collection.objects.all(),
        method="recursive_photo_filter",
    )

    def recursive_photo_filter(self, queryset, name, value):
        models.Photograph.objects.raw(
            f"WITH RECURSIVE ch_coll(id) AS ( SELECT id, label, parent_collection_id FROM collection_collection WHERE parent_collection_id = {value.id} UNION SELECT ch.id, ch.label, ch.parent_collection_id FROM collection_collection AS ch, ch_coll AS c WHERE ch.parent_collection_id=c.id ) SELECT DISTINCT photograph_photograph.id, photograph_photograph.image_path, photograph_photograph.date_early, photograph_photograph.date_late, photograph_photograph.digitized_date, photograph_photograph.taken_by_id, photograph_photograph.collection_id collection FROM photograph_photograph INNER JOIN ch_coll ON (photograph_photograph.collection_id = ch_coll.id)"
        )


class PhotographViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Photograph.objects.all()
    serializer_class = serializers.PhotographDetailSerializer
    serializer_action_classes = {"list": serializers.PhotographListSerializer}
