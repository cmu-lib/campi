from rest_framework import serializers
from tagging import models
import campi.serializers
import cv.serializers
import photograph.serializers


class TagSerializer(serializers.ModelSerializer):
    n_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Tag
        fields = ["id", "label", "n_images"]


class TaggingTaskSerializer(serializers.ModelSerializer):
    tag = TagSerializer()
    pytorch_model = cv.serializers.PytorchModelListSerializer()
    assigned_user = campi.serializers.UserSerializer()

    class Meta:
        model = models.TaggingTask
        fields = ["id", "tag", "pytorch_model", "assigned_user"]


class TaggingDecisionSerializer(serializers.ModelSerializer):
    task = TaggingTaskSerializer()
    photograph = photograph.serializers.PhotographListSerializer()

    class Meta:
        model = models.TaggingDecision
        fields = ["id", "task", "photograph", "is_applicable"]


class PhotographTagPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhotographTag
        fields = ["tag", "photograph"]
