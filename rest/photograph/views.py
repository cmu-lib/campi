from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from photograph import serializers, models
from django_filters import rest_framework as filters
from argus.views import GetSerializerClassMixin


class PhotographViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.Photograph.objects.all()
    serializer_class = serializers.PhotographDetailSerializer
    serializer_action_classes = {"list": serializers.PhotographListSerializer}


# class FolderViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
#     queryset = models.Folder.objects.all()
#     serializer_class = serializers.FolderDetailSerializer
#     serializer_action_classes = {"list": serializers.FolderListSerializer}


# class BundleViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
#     queryset = models.Bundle.objects.all()
#     serializer_class = serializers.BundleDetailSerializer
#     serializer_action_classes = {"list": serializers.BundleListSerializer}


# class DocumentFilter(filters.FilterSet):
#     topic_model = filters.ModelChoiceFilter(
#         queryset=text_models.TopicModel.objects.all(),
#         field_name="topic_models",
#         widget=forms.TextInput,
#     )
#     document_format = filters.ModelChoiceFilter(
#         queryset=metadata_models.DocumentFormat.objects.all(),
#         field_name="record__document_format",
#     )
#     document_subject = filters.ModelChoiceFilter(
#         queryset=metadata_models.DocumentSubject.objects.all(),
#         field_name="record__document_subject",
#     )
#     label = filters.CharFilter(lookup_expr="icontains")
#     topics = filters.ModelChoiceFilter(queryset=text_models.Topic.objects.all())


# class DocumentViewSet(GetSerializerClassMixin, viewsets.ModelViewSet):
#     queryset = models.Document.objects.all()
#     serializer_class = serializers.DocumentDetailSerializer
#     serializer_action_classes = {"list": serializers.DocumentListSerializer}
#     filterset_class = DocumentFilter


# class PageViewSet(viewsets.ModelViewSet):
#     queryset = models.Page.objects.all()
#     serializer_class = serializers.PageSerializer
