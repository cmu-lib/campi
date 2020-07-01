from rest_framework import serializers
from collection import models as collection_models
from photograph import models as photograph_models
from rest_framework_recursive.fields import RecursiveField


class DirectoryParentSerializer(serializers.ModelSerializer):
    parent_directory = RecursiveField()

    class Meta:
        model = collection_models.Directory
        fields = ["id", "url", "label", "parent_directory"]


class DirectoryListSerializer(serializers.ModelSerializer):
    n_images = serializers.IntegerField(read_only=True)
    parent_directory = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = collection_models.Directory
        fields = ["id", "url", "label", "description", "n_images", "parent_directory"]


class DirectoryDetailSerializer(serializers.ModelSerializer):
    parent_directory = DirectoryParentSerializer()
    child_directories = DirectoryListSerializer(many=True)
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = collection_models.Directory
        fields = [
            "id",
            "url",
            "label",
            "description",
            "parent_directory",
            "child_directories",
            "n_images",
        ]


class JobListSerializer(serializers.ModelSerializer):
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = collection_models.Job
        fields = [
            "id",
            "url",
            "label",
            "description",
            "job_code",
            "date_start",
            "date_end",
            "n_images",
        ]


class JobDetailSerializer(serializers.ModelSerializer):
    n_images = serializers.IntegerField(read_only=True)
    tags = serializers.SlugRelatedField(read_only=True, slug_field="label", many=True)

    class Meta:
        model = collection_models.Job
        fields = [
            "id",
            "url",
            "label",
            "description",
            "job_code",
            "date_start",
            "date_end",
            "n_images",
            "tags",
        ]


class JobTagSerializer(serializers.ModelSerializer):
    n_jobs = serializers.IntegerField(read_only=True)
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = collection_models.JobTag
        fields = ["id", "url", "label", "description", "n_jobs", "n_images"]


class JobTagIdList(serializers.Serializer):
    job_tags = serializers.PrimaryKeyRelatedField(
        queryset=collection_models.JobsTags.objects.all(), many=True
    )
