from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from django.db.models import (
    Count,
    Exists,
    F,
    Q,
    Value,
    Prefetch,
    OuterRef,
    ExpressionWrapper,
    BooleanField,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from cv import models, serializers
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
from photograph.views import prepare_photograph_qs
from sklearn import metrics
import numpy
import photograph
import collection
import tagging
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
    queryset_action_classes = {"list": queryset, "detail": queryset}
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

    @action(
        detail=True, methods=["post"], name="Get nearest neighbors for a given object"
    )
    def get_nn(self, request, pk=None):
        idx = self.get_object()
        raw_nn_req = serializers.PytorchModelGetNNSerializer(data=request.data)
        if raw_nn_req.is_valid():
            validated_data = raw_nn_req.validated_data
            nn = idx.get_nn(
                photo=validated_data["photograph"],
                n_neighbors=validated_data["n_neighbors"],
            )
            serialized_neighbors = photograph.serializers.PhotographDistanceListSerializer(
                photograph.views.prepare_photograph_qs(nn),
                many=True,
                context={"request": request},
            ).data
            return Response(serialized_neighbors, status.HTTP_200_OK)
        else:
            return Response(raw_nn_req.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseMatchRunViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.CloseMatchRun.objects.select_related("pytorch_model").annotate(
        n_sets=Count("close_match_sets", distinct=True),
        n_complete=Count(
            "close_match_sets",
            filter=Q(close_match_sets__user_last_modified__isnull=False),
        ),
    )
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
            n_approved=Count(
                "memberships",
                filter=Q(memberships__state=models.CloseMatchSetMembership.ACCEPTED),
            )
        ).filter(n_approved__gte=2, user_last_modified__isnull=False)

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
                "close_match_set__has_duplicates",
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
            "has_duplicates",
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
                    match["close_match_set__has_duplicates"],
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
    redundant = filters.BooleanFilter()
    overlapping = filters.BooleanFilter()
    unreviewed = filters.BooleanFilter(
        field_name="user_last_modified", lookup_expr="isnull"
    )
    memberships = filters.ModelChoiceFilter(
        queryset=photograph.models.Photograph.objects.all(),
        help_text="Photograph within this proposed match set",
        field_name="memberships__photograph",
    )


class CloseMatchSetViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    prefetched_photographs = prepare_photograph_qs(
        photograph.models.Photograph.objects.all()
    )
    memberships = Prefetch(
        "memberships",
        queryset=models.CloseMatchSetMembership.objects.prefetch_related(
            Prefetch("photograph", queryset=prefetched_photographs)
        ).order_by("-core", "distance"),
    )
    representative_photograph = Prefetch(
        "representative_photograph", queryset=prefetched_photographs
    )
    secondary_memberships = models.CloseMatchSetMembership.objects.filter(
        close_match_set=OuterRef("pk"), core=False
    )
    queryset = (
        models.CloseMatchSet.objects.select_related(
            "close_match_run", "close_match_run__pytorch_model", "user_last_modified",
        )
        .annotate(
            n_images=Count("memberships"),
            n_unreviewed_images=Count(
                "memberships",
                filter=Q(
                    memberships__state=models.CloseMatchSetMembership.NOT_REVIEWED
                ),
            ),
            n_redundant_images=Count(
                "memberships",
                filter=Q(memberships__state=models.CloseMatchSetMembership.OTHER_SET)
                | Q(memberships__state=models.CloseMatchSetMembership.EXCLUDED),
            ),
            n_valid_images=F("n_images") - F("n_redundant_images"),
            redundant=ExpressionWrapper(
                Q(n_valid_images__lte=1), output_field=BooleanField()
            ),
            overlapping=Exists(secondary_memberships),
        )
        .prefetch_related(memberships, representative_photograph)
    )
    serializer_class = serializers.CloseMatchSetSerializer
    filterset_class = CloseMatchSetFilter
    ordering_fields = ["last_updated", "n_images", "n_unreviewed_images"]

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
            res = close_match_set.approve(
                accepted_memberships=approval_data["accepted_memberships"],
                rejected_memberships=approval_data["rejected_memberships"],
                excluded_memberships=approval_data["excluded_memberships"],
                representative_photograph=approval_data["representative_photograph"],
                has_duplicates=approval_data["has_duplicates"],
                user=request.user,
            )
            return Response(res, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(
                raw_approval_data.errors, status=status.HTTP_400_BAD_REQUEST
            )


class CloseMatchSetMembershipViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.CloseMatchSetMembership.objects.select_related(
        "photograph", "photograph__directory", "photograph__job"
    ).all()
    serializer_class = serializers.CloseMatchSetMembershipSerializer
    serializer_action_classes = {
        "list": serializers.CloseMatchSetMembershipSerializer,
        "detail": serializers.CloseMatchSetMembershipSerializer,
        "create": serializers.CloseMatchSetMembershipPostSerializer,
        "update": serializers.CloseMatchSetMembershipPostSerializer,
        "partial_update": serializers.CloseMatchSetMembershipPostSerializer,
    }

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Override the basic POST method to calculate the distance on the fly
        """
        membership_serializer = self.get_serializer_class()(data=request.data)
        if membership_serializer.is_valid():
            obj = membership_serializer.save()
            embedding_model = obj.close_match_set.close_match_run.pytorch_model
            first_photo = obj.close_match_set.memberships.first().photograph
            target_photo = obj.photograph

            first_embeddings = models.Embedding.objects.get(
                photograph=first_photo, pytorch_model=embedding_model
            ).array
            target_embeddings = models.Embedding.objects.get(
                photograph=target_photo, pytorch_model=embedding_model
            ).array

            cosine_distance = list(
                metrics.pairwise.cosine_distances(
                    numpy.array([first_embeddings]), numpy.array([target_embeddings])
                )[
                    0,
                ]
            )[0]

            obj.distance = cosine_distance
            obj.core = False
            obj.user_added = True
            obj.save()
            return Response(
                self.get_serializer_class()(obj, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                membership_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

