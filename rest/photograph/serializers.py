from rest_framework import serializers
from photograph import models
import collection.serializers
import tagging.models
import campi.serializers


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = tagging.models.Tag
        fields = ["id", "label"]


class PhotographTagSerializer(serializers.ModelSerializer):
    user_last_modified = campi.serializers.UserSerializer()
    tag = TagSerializer()

    class Meta:
        model = tagging.models.PhotographTag
        fields = ["tag", "user_last_modified", "last_updated"]


class PhotographDetailSerializer(serializers.HyperlinkedModelSerializer):
    directory = collection.serializers.DirectoryDetailSerializer()
    job = collection.serializers.JobDetailSerializer()
    tags = PhotographTagSerializer(many=True)

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


class PhotographListSerializer(serializers.HyperlinkedModelSerializer):
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
