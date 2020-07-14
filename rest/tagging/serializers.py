from rest_framework import serializers
from tagging import models
import campi.serializers
import cv.serializers
import photograph.serializers


class FlatTagSerializer(serializers.ModelSerializer):
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Tag
        fields = ["id", "label", "n_images"]


class TaggingTaskSerializer(serializers.ModelSerializer):
    tag = FlatTagSerializer()
    pytorch_model = cv.serializers.PytorchModelListSerializer()
    assigned_user = campi.serializers.UserSerializer()

    class Meta:
        model = models.TaggingTask
        fields = ["id", "tag", "pytorch_model", "assigned_user"]


class FlatTaggingTaskSerializer(serializers.ModelSerializer):
    pytorch_model = cv.serializers.PytorchModelListSerializer()
    assigned_user = campi.serializers.UserSerializer()

    class Meta:
        model = models.TaggingTask
        fields = ["id", "pytorch_model", "assigned_user"]


class TaggingTaskPostSerializer(serializers.ModelSerializer):
    assigned_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = models.TaggingTask
        fields = ["id", "tag", "pytorch_model", "assigned_user"]


class TagSerializer(serializers.ModelSerializer):
    n_images = serializers.IntegerField(read_only=True)
    tasks = FlatTaggingTaskSerializer(many=True, read_only=True)

    class Meta:
        model = models.Tag
        fields = ["id", "label", "n_images", "tasks"]


class TaggingDecisionSerializer(serializers.ModelSerializer):
    user_created = campi.serializers.UserSerializer(
        default=serializers.CurrentUserDefault()
    )
    other_tagged_photos = serializers.SerializerMethodField()

    def get_other_tagged_photos(self, obj):
        all_decisions = obj.photograph.get_close_matches().values_list(
            "id", "decisions", "decisions__task", "decisions__is_applicable"
        )
        return [
            {
                "photograph": {"id": d[0]},
                "tagging_decision": {"id": d[1], "task": d[2], "is_applicable": d[3]},
            }
            for d in all_decisions
        ]

    class Meta:
        model = models.TaggingDecision
        fields = [
            "id",
            "task",
            "photograph",
            "is_applicable",
            "user_created",
            "other_tagged_photos",
        ]


class PhotographTagPostSerializer(serializers.ModelSerializer):
    user_last_modified = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    other_tagged_photos = serializers.SerializerMethodField()

    def get_other_tagged_photos(self, obj):
        return obj.photograph.get_close_matches().values_list("id", flat=True)

    class Meta:
        model = models.PhotographTag
        fields = [
            "id",
            "url",
            "tag",
            "photograph",
            "user_last_modified",
            "other_tagged_photos",
        ]
