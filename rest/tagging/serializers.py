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
    class Meta:
        model = models.TaggingDecision
        fields = ["id", "task", "photograph", "is_applicable", "user_created"]


class PhotographTagPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhotographTag
        fields = ["id", "url", "tag", "photograph"]
