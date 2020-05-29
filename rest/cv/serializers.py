from rest_framework import serializers
from cv import models
import photograph.models


class PytorchModelListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PyTorchModel
        fields = ["id", "url", "label", "n_dimensions"]


class AnnoyIdxListSerializer(serializers.HyperlinkedModelSerializer):
    n_images = serializers.IntegerField(read_only=True)
    pytorch_model = PytorchModelListSerializer()

    class Meta:
        model = models.AnnoyIdx
        fields = ["id", "url", "pytorch_model", "n_trees", "n_images", "index_built"]


class AnnoyIdxGetNNSerializer(serializers.Serializer):
    photograph = serializers.PrimaryKeyRelatedField(
        queryset=photograph.models.Photograph.objects.all(), required=True
    )
    n_neighbors = serializers.IntegerField(required=True)
