from rest_framework import serializers
from photograph import models
import collection.serializers
import tagging.models
import campi.serializers


class FlatTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = tagging.models.Tag
        fields = ["id", "label"]


class PhotographTagSerializer(serializers.ModelSerializer):
    user_last_modified = campi.serializers.UserSerializer()
    tag = FlatTagSerializer()

    class Meta:
        model = tagging.models.PhotographTag
        fields = ["tag", "user_last_modified", "last_updated"]


class PhotographDetailSerializer(serializers.ModelSerializer):
    directory = collection.serializers.DirectoryDetailSerializer()
    job = collection.serializers.JobDetailSerializer()
    photograph_tags = PhotographTagSerializer(many=True)

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "filename",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
        ]


class PhotographListSerializer(serializers.ModelSerializer):
    directory = collection.serializers.DirectoryListSerializer()
    job = collection.serializers.JobListSerializer()
    photograph_tags = PhotographTagSerializer(many=True)

    class Meta:
        model = models.Photograph
        fields = [
            "id",
            "url",
            "label",
            "image",
            "filename",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
        ]
