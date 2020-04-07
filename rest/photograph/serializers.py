from rest_framework import serializers
from photograph import models
from collection import serializers as collection_serializers


class PhotographDetailSerializer(serializers.HyperlinkedModelSerializer):
    collection = collection_serializers.CollectionDetailSerializer()

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "date_early",
            "date_late",
            "digitized_date",
            "taken_by",
            "depicts",
            "collection",
        ]


class PhotographListSerializer(serializers.HyperlinkedModelSerializer):
    collection = collection_serializers.CollectionListSerializer()

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "date_early",
            "date_late",
            "digitized_date",
            "collection",
        ]
