from rest_framework import serializers
from cv import models
import photograph.models
from campi.serializers import UserSerializer
from rest_framework.reverse import reverse


class PytorchModelListSerializer(serializers.HyperlinkedModelSerializer):
    feature_matrix = serializers.SerializerMethodField()

    def get_feature_matrix(self, obj):
        return reverse(
            "pytorchmodel-feature-matrix", [obj.id], request=self.context["request"]
        )

    class Meta:
        model = models.PyTorchModel
        fields = ["id", "url", "label", "n_dimensions", "feature_matrix"]


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
    n_sets = serializers.IntegerField(read_only=True)
    n_complete = serializers.IntegerField(read_only=True)
    download_matches = serializers.SerializerMethodField()

    def get_download_matches(self, obj):
        return reverse(
            "closematchrun-download-matches", [obj.id], request=self.context["request"]
        )

    class Meta:
        model = models.CloseMatchRun
        fields = [
            "id",
            "url",
            "created_on",
            "pytorch_model",
            "cutoff_distance",
            "exclude_future_distance",
            "min_samples",
            "n_sets",
            "n_complete",
            "download_matches",
        ]


class CloseMatchSetMembershipPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CloseMatchSetMembership
        fields = [
            "id",
            "close_match_set",
            "photograph",
            "core",
            "distance",
            "accepted",
            "invalid",
        ]


class CloseMatchSetMembershipSerializer(serializers.HyperlinkedModelSerializer):
    photograph = photograph.serializers.PhotographListSerializer(many=False)

    class Meta:
        model = models.CloseMatchSetMembership
        fields = [
            "id",
            "close_match_set",
            "photograph",
            "core",
            "distance",
            "accepted",
            "invalid",
        ]


class CloseMatchSetSerializer(serializers.HyperlinkedModelSerializer):
    close_match_run = CloseMatchRunSerializer(many=False)
    representative_photograph = photograph.serializers.PhotographListSerializer(
        many=False
    )
    memberships = CloseMatchSetMembershipSerializer(many=True)
    user_last_modified = UserSerializer(many=False)
    invalid = serializers.BooleanField(read_only=True)
    overlapping = serializers.BooleanField(read_only=True)
    n_images = serializers.IntegerField(read_only=True)
    n_valid_images = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.CloseMatchSet
        fields = [
            "id",
            "close_match_run",
            "representative_photograph",
            "memberships",
            "user_last_modified",
            "last_updated",
            "invalid",
            "n_images",
            "n_valid_images",
            "overlapping",
        ]


class CloseMatchSetApprovalSerializer(serializers.Serializer):
    accepted_memberships = serializers.PrimaryKeyRelatedField(
        queryset=models.CloseMatchSetMembership.objects.all(), many=True
    )
    eliminated_photographs = serializers.PrimaryKeyRelatedField(
        queryset=photograph.models.Photograph.objects.all(), many=True
    )
    representative_photograph = serializers.PrimaryKeyRelatedField(
        queryset=photograph.models.Photograph.objects.all(), many=False, allow_null=True
    )
