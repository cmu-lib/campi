from django.http import HttpResponse
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
import csv


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

    @action(
        detail=True,
        methods=["get"],
        name="Download a CSV with IIIF links and features generated by this model",
    )
    def feature_matrix(self, request, pk=None):
        pytorch_model = self.get_object()
        all_embeddings = pytorch_model.embeddings.select_related("photograph").all()
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = f"attachment; filename={pytorch_model.label}_embeddings.csv"
        writer = csv.writer(response)
        headers = ["image_url"] + [
            f"f{i}" for i in range(1, pytorch_model.n_dimensions + 1)
        ]
        writer.writerow(headers)
        for img in all_embeddings:
            writer.writerow([img.photograph.full_image] + img.array)

        return response


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

    @action(detail=True, methods=["get"])
    def download_matches(
        self,
        request,
        pk=None,
        name="Download a CSV with filenames and their approved match groups",
    ):
        close_match_run = self.get_object()
        useful_match_sets = close_match_run.close_match_sets.annotate(
            n_approved=Count("memberships", filter=Q(memberships__accepted=True))
        ).filter(n_approved__gte=2, user_last_modified__isnull=False, invalid=False)

        all_memberships = (
            models.CloseMatchSetMembership.objects.filter(
                close_match_set__in=useful_match_sets
            )
            .order_by("id")
            .distinct()
            .values(
                "close_match_set__id",
                "photograph__id",
                "photograph__original_server_path",
                "close_match_set__representative_photograph__id",
                "close_match_set__user_last_modified__username",
                "close_match_set__last_updated",
            )
        )
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=close_match_sets.csv"
        writer = csv.writer(response)
        headers = [
            "photograph_file_name",
            "photograph_id",
            "set_id",
            "is_primary",
            "approving_user",
            "date_approved",
        ]
        writer.writerow(headers)
        for match in all_memberships:
            writer.writerow(
                [
                    match["photograph__original_server_path"],
                    match["photograph__id"],
                    match["close_match_set__id"],
                    match["close_match_set__representative_photograph__id"]
                    == match["photograph__id"],
                    match["close_match_set__user_last_modified__username"],
                    match["close_match_set__last_updated"],
                ]
            )

        return response


class CloseMatchSetFilter(filters.FilterSet):
    close_match_run = filters.ModelChoiceFilter(
        queryset=models.CloseMatchRun.objects.all(),
        help_text="The run that created this match set",
    )
    invalid = filters.BooleanFilter()
    not_signed_off = filters.BooleanFilter(method="has_user_signed_off")
    memberships = filters.ModelChoiceFilter(
        queryset=photograph.models.Photograph.objects.all(),
        help_text="Photograph within this proposed match set",
        field_name="memberships__photograph",
    )

    def has_user_signed_off(self, queryset, name, value):
        if value:
            return queryset.filter(user_last_modified__isnull=True)
        else:
            return queryset


class CloseMatchSetViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = (
        models.CloseMatchSet.objects.select_related(
            "close_match_run",
            "close_match_run__pytorch_model",
            "close_match_run__annoy_idx",
            "representative_photograph",
            "representative_photograph__directory",
            "representative_photograph__job",
            "user_last_modified",
        )
        .annotate(n_images=Count("memberships", filter=Q(memberships__invalid=False)))
        .prefetch_related(
            "memberships",
            "memberships__photograph__directory",
            "memberships__photograph__job",
        )
    )
    serializer_class = serializers.CloseMatchSetSerializer
    filterset_class = CloseMatchSetFilter
    ordering_fields = ["last_updated", "n_images"]

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

            # Once saved, mark invalid all accepted photos from other memberships THAT HAVEN'T BEEN ACCEPTED YET
            accepted_photographs = photograph.models.Photograph.objects.filter(
                close_match_memberships__in=close_match_set.memberships.filter(
                    accepted=True
                ).all()
            ).distinct()
            n_memberships_deleted = (
                models.CloseMatchSetMembership.objects.filter(
                    close_match_set__close_match_run=close_match_set.close_match_run,
                    close_match_set__user_last_modified__isnull=True,
                    photograph__in=accepted_photographs,
                )
                .all()
                .update(invalid=True)
            )

            # Mark invalid all memberships in this run with the invalidated photos
            n_memberships_eliminated = (
                models.CloseMatchSetMembership.objects.filter(
                    close_match_set__close_match_run=close_match_set.close_match_run,
                    photograph__in=approval_data["eliminated_photographs"],
                )
                .all()
                .update(invalid=True)
            )

            # Mark invalid any sets that no longer have 2 or more photos, or where the seed photo was any of the accepted photos
            n_sets_too_small = (
                models.CloseMatchSet.objects.annotate(
                    n_memberships=Count(
                        "memberships",
                        filter=Q(memberships__invalid=False),
                        distinct=True,
                    )
                )
                .filter(
                    invalid=False,
                    n_memberships__lt=2,
                    close_match_run=close_match_set.close_match_run,
                )
                .update(invalid=True, user_last_modified=request.user)
            )

            res = {
                "invalidations": {
                    "n_memberships_deleted": n_memberships_deleted,
                    "n_memberships_eliminated": n_memberships_eliminated,
                    "n_sets_too_small": n_sets_too_small,
                }
            }

            return Response(res, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(
                raw_approval_data.errors, status=status.HTTP_400_BAD_REQUEST
            )
