from rest_framework import serializers
from collection import models as collection_models
from photograph import models as photograph_models
from rest_framework_recursive.fields import RecursiveField


class DirectoryParentSerializer(serializers.HyperlinkedModelSerializer):
    parent_directory = RecursiveField()

    class Meta:
        model = collection_models.Directory
        fields = ["id", "url", "label", "parent_directory"]


class DirectoryListSerializer(serializers.HyperlinkedModelSerializer):
    search_photographs = serializers.URLField(read_only=True)
    n_images = serializers.IntegerField(read_only=True)
    parent_directory = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = collection_models.Directory
        fields = [
            "id",
            "url",
            "label",
            "n_images",
            "search_photographs",
            "parent_directory",
        ]


class DirectoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    parent_directory = DirectoryParentSerializer()
    child_directories = DirectoryListSerializer(many=True)
    search_photographs = serializers.URLField(read_only=True)

    class Meta:
        model = collection_models.Directory
        fields = [
            "id",
            "url",
            "label",
            "description",
            "search_photographs",
            "parent_directory",
            "child_directories",
        ]


class JobListSerializer(serializers.HyperlinkedModelSerializer):
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


class JobDetailSerializer(serializers.HyperlinkedModelSerializer):
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


class JobTagSerializer(serializers.HyperlinkedModelSerializer):
    n_jobs = serializers.IntegerField(read_only=True)
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = collection_models.JobTag
        fields = ["id", "url", "label", "description", "n_jobs", "n_images"]


class JobTagIdList(serializers.Serializer):
    job_tags = serializers.PrimaryKeyRelatedField(
        queryset=collection_models.JobsTags.objects.all(), many=True
    )
