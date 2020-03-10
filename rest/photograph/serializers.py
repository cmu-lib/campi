from rest_framework import serializers
from photograph import models


class PhotographDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Photograph
        fields = [
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


class PhotographListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Photograph
        fields = [
            "url",
            "label",
            "image",
            "date_early",
            "date_late",
            "digitized_date",
            "collection",
        ]
