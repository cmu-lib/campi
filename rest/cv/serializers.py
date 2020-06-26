from rest_framework import serializers
from cv import models
from photograph.serializers import PhotographListSerializer
import photograph.models
from campi.serializers import UserSerializer
from rest_framework.reverse import reverse


class PytorchModelListSerializer(serializers.ModelSerializer):
    feature_matrix = serializers.SerializerMethodField()

    def get_feature_matrix(self, obj):
        return reverse(
            "pytorchmodel-feature-matrix", [obj.id], request=self.context["request"]
        )

    class Meta:
        model = models.PyTorchModel
        fields = ["id", "url", "label", "n_dimensions", "feature_matrix"]


class AnnoyIdxFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnnoyIdx
        fields = ["id", "url", "n_trees", "index_built"]


class AnnoyIdxListSerializer(serializers.ModelSerializer):
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


class CloseMatchRunSerializer(serializers.ModelSerializer):
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
        fields = ["id", "close_match_set", "photograph", "core", "state"]


class CloseMatchSetMembershipSerializer(serializers.ModelSerializer):
    photograph = PhotographListSerializer(many=False)

    class Meta:
        model = models.CloseMatchSetMembership
        fields = [
            "id",
            "close_match_set",
            "photograph",
            "core",
            "distance",
            "state",
            "user_added",
        ]


class CloseMatchSetSerializer(serializers.ModelSerializer):
    close_match_run = CloseMatchRunSerializer(many=False)
    representative_photograph = PhotographListSerializer(many=False)
    memberships = CloseMatchSetMembershipSerializer(many=True)
    user_last_modified = UserSerializer(many=False)
    invalid = serializers.BooleanField(read_only=True)
    overlapping = serializers.BooleanField(read_only=True)
    n_images = serializers.IntegerField(read_only=True)
    n_unreviewed_images = serializers.IntegerField(read_only=True)
    n_redundant_images = serializers.IntegerField(read_only=True)
    redundant = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.CloseMatchSet
        fields = [
            "id",
            "close_match_run",
            "representative_photograph",
            "memberships",
            "user_last_modified",
            "last_updated",
            "has_duplicates",
            "invalid",
            "n_images",
            "n_unreviewed_images",
            "n_redundant_images",
            "overlapping",
            "redundant",
        ]


class CloseMatchSetApprovalSerializer(serializers.Serializer):
    accepted_memberships = serializers.PrimaryKeyRelatedField(
        queryset=models.CloseMatchSetMembership.objects.all(), many=True
    )
    rejected_memberships = serializers.PrimaryKeyRelatedField(
        queryset=models.CloseMatchSetMembership.objects.all(), many=True
    )
    excluded_memberships = serializers.PrimaryKeyRelatedField(
        queryset=models.CloseMatchSetMembership.objects.all(), many=True
    )
    representative_photograph = serializers.PrimaryKeyRelatedField(
        queryset=photograph.models.Photograph.objects.all(), many=False
    )
    has_duplicates = serializers.BooleanField()


class FullDistanceSerializer(serializers.ModelSerializer):
    # photograph = PhotographListSerializer(many=False)
    target_photograph = PhotographListSerializer(many=False)

    class Meta:
        model = models.FullDistance
        fields = ["id", "url", "photograph", "target_photograph", "distance"]

