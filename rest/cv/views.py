from django.db import transaction
from django.db.models import Count, Q, BooleanField, ExpressionWrapper, Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from cv import models, serializers
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
import photograph
import collection


class PyTorchModelFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="models with this text in their label", lookup_expr="icontains"
    )


class PytorchModelViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.PyTorchModel.objects
    serializer_class = serializers.PytorchModelListSerializer
    serializer_action_classes = {
        "list": serializers.PytorchModelListSerializer,
        "detail": serializers.PytorchModelListSerializer,
    }
    filterset_class = PyTorchModelFilter
    queryset_action_classes = {
        "list": queryset.prefetch_related("pytorch_model_ann_indices"),
        "detail": queryset.prefetch_related("pytorch_model_ann_indices"),
    }
    ordering_fields = ["label", "date_created", "date_modified"]


class AnnoyIdxFilter(filters.FilterSet):
    pytorch_model = filters.ModelChoiceFilter(
        queryset=models.PyTorchModel.objects.all(),
        help_text="Indices built from this model's embeddings",
    )


class AnnoyIdxViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.AnnoyIdx.objects.select_related("pytorch_model").annotate(
        n_images=Count("indexed_embeddings", distinct=True)
    )
    filterset_class = AnnoyIdxFilter
    serializer_class = serializers.AnnoyIdxListSerializer
    serializer_action_classes = {
        "list": serializers.AnnoyIdxListSerializer,
        "detail": serializers.AnnoyIdxListSerializer,
    }
    queryset_action_classes = {"list": queryset, "detail": queryset}

    @action(
        detail=True, methods=["post"], name="Get nearest neighbors for a given object"
    )
    def get_nn(self, request, pk=None):
        idx = self.get_object()
        raw_nn_req = serializers.AnnoyIdxGetNNSerializer(data=request.data)
        if raw_nn_req.is_valid():
            validated_data = raw_nn_req.validated_data
            nn = idx.get_nn(
                photo=validated_data["photograph"],
                n_neighbors=validated_data["n_neighbors"],
            )
            serialized_neighbors = photograph.serializers.PhotographListSerializer(
                nn["photographs"], many=True, context={"request": request}
            ).data
            for i, entry in enumerate(serialized_neighbors):
                entry["distance"] = nn["distances"][i]
            return Response(serialized_neighbors, status.HTTP_200_OK)
        else:
            return Response(raw_nn_req.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseMatchRunViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.CloseMatchRun.objects.select_related(
        "pytorch_model", "annoy_idx"
    ).annotate(n_sets=Count("close_match_sets", distinct=True))
    serializer_class = serializers.CloseMatchRunSerializer


class CloseMatchSetFilter(filters.FilterSet):
    close_match_run = filters.ModelChoiceFilter(
        queryset=models.CloseMatchRun.objects.all(),
        help_text="The run that created this match set",
    )
    signed_off = filters.BooleanFilter(method="has_user_signed_off")

    def has_user_signed_off(self, queryset, name, value):
        if value:
            return queryset.filter(user_last_modified__isnull=False)
        else:
            return queryset


class CloseMatchSetViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = (
        models.CloseMatchSet.objects.select_related(
            "close_match_run",
            "close_match_run__pytorch_model",
            "close_match_run__annoy_idx",
            "seed_photograph",
            "seed_photograph__directory",
            "seed_photograph__job",
            "representative_photograph",
            "representative_photograph__directory",
            "representative_photograph__job",
            "user_last_modified",
        )
        .annotate(n_images=Count("photographs", distinct=True))
        .prefetch_related(
            "memberships",
            "memberships__photograph__directory",
            "memberships__photograph__job",
        )
    )
    serializer_class = serializers.CloseMatchSetSerializer
    filterset_class = CloseMatchSetFilter
    ordering_fields = ["last_updated", "seed_photo"]

    @transaction.atomic
    @action(detail=True, methods=["patch"])
    def approve(self, request, pk=None):
        close_match_set = self.get_object()
        raw_approval_data = serializers.CloseMatchSetApprovalSerializer(
            data=request.data
        )
        if raw_approval_data.is_valid():
            approval_data = raw_approval_data.validated_data
            # Set memberships to false, then updated selected ones
            close_match_set.memberships.all().update(accepted=False)
            for m in approval_data["accepted_memberships"]:
                m.accepted = True
                m.save()

            # Set representative photograph on set
            close_match_set.representative_photograph = approval_data[
                "representative_photograph"
            ]

            # Tag this set with the user who has sent the approval notice
            close_match_set.user_last_modified = request.user
            close_match_set.save()

            # Once saved, remove all accepted photos from other memberships THAT HAVEN'T BEEN ACCEPTED YET
            accepted_photographs = photograph.models.Photograph.objects.filter(
                close_match_memberships__in=close_match_set.memberships.filter(
                    accepted=True
                ).all()
            ).distinct()
            n_memberships_deleted = (
                models.CloseMatchSetMembership.objects.filter(
                    close_match_set__user_last_modified__isnull=True,
                    photograph__in=accepted_photographs,
                )
                .all()
                .delete()
            )

            # Delete any sets that no longer have 2 or more photos, or where the seed photo was any of the accepted photos
            n_sets_too_small = (
                models.CloseMatchSet.objects.annotate(
                    n_memberships=Count("memberships", distinct=True)
                )
                .filter(n_memberships__lt=2)
                .delete()
            )

            n_sets_seed = (
                models.CloseMatchSet.objects.filter(
                    user_last_modified__isnull=True,
                    seed_photograph__in=accepted_photographs,
                )
                .distinct()
                .delete()
            )

            res = {
                "n_memberships_deleted": n_memberships_deleted,
                "n_sets_too_small": n_sets_too_small,
                "n_sets_seed": n_sets_seed,
            }

            return Response(res, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(
                raw_approval_data.errors, status=status.HTTP_400_BAD_REQUEST
            )
