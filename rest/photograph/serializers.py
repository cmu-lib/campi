from rest_framework import serializers
from photograph import models
from collection import serializers as collection_serializers


class PhotographDetailSerializer(serializers.HyperlinkedModelSerializer):
    directory = collection_serializers.CollectionDetailSerializer()

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
        ]


class PhotographListSerializer(serializers.HyperlinkedModelSerializer):
    directory = collection_serializers.CollectionListSerializer()

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
        ]
