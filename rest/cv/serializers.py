from rest_framework import serializers
from cv import models
import photograph.models


class PytorchModelListSerializer(serializers.HyperlinkedModelSerializer):
    pytorch_model_ann_indices = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = models.PyTorchModel
        fields = ["id", "url", "label", "n_dimensions", "pytorch_model_ann_indices"]


class AnnoyIdxListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.AnnoyIdx
        fields = ["id", "url", "pytorch_model", "n_trees", "index_built"]


class AnnoyIdxGetNNSerializer(serializers.Serializer):
    photograph = serializers.PrimaryKeyRelatedField(
        queryset=photograph.models.Photograph.objects.all(), required=True
    )
    n_neighbors = serializers.IntegerField(required=True)
