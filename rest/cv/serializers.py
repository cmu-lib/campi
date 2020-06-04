from rest_framework import serializers
from cv import models
import photograph.models


class PytorchModelListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PyTorchModel
        fields = ["id", "url", "label", "n_dimensions"]


class AnnoyIdxFlatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.AnnoyIdx
        fields = ["id", "url", "n_trees", "index_built"]


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


class CloseMatchRunSerializer(serializers.HyperlinkedModelSerializer):
    pytorch_model = PytorchModelListSerializer(many=False)
    annoy_idx = AnnoyIdxFlatSerializer(many=False)
    n_sets = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.CloseMatchRun
        fields = [
            "id",
            "url",
            "pytorch_model",
            "annoy_idx",
            "max_neighbors",
            "cutoff_distance",
            "exclude_future_distance",
            "n_sets",
        ]


class CloseMatchSetMembershipSerializer(serializers.HyperlinkedModelSerializer):
    photograph = photograph.serializers.PhotographListSerializer(many=False)

    class Meta:
        model = models.CloseMatchSetMembership
        fields = ["id", "photograph", "distance"]


class CloseMatchSetSerializer(serializers.HyperlinkedModelSerializer):
    close_match_run = CloseMatchRunSerializer(many=False)
    seed_photograph = photograph.serializers.PhotographListSerializer(many=False)
    memberships = CloseMatchSetMembershipSerializer(many=True)

    class Meta:
        model = models.CloseMatchSet
        fields = ["id", "close_match_run", "seed_photograph", "memberships"]
