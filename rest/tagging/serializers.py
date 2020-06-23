from rest_framework import serializers
from tagging import models
import campi
import cv
import photograph


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ["id", "label"]


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
