from rest_framework import serializers
from photograph import models
import collection.serializers


class PhotographDetailSerializer(serializers.HyperlinkedModelSerializer):
    directory = collection.serializers.DirectoryDetailSerializer()
    job = collection.serializers.JobDetailSerializer()

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
        ]


class PhotographListSerializer(serializers.HyperlinkedModelSerializer):
    directory = collection.serializers.DirectoryListSerializer()
    job = collection.serializers.JobDetailSerializer()

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
        ]
