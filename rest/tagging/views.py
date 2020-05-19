from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from collection import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin


class CollectionViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Collection.objects.all()
    serializer_class = serializers.CollectionDetailSerializer
    serializer_action_classes = {"list": serializers.CollectionListSerializer}
    queryset_action_classes = {"list": self.queryset, "detail": None}
