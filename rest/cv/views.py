from django.db import transaction
from django.db.models import Count, Q, BooleanField, ExpressionWrapper
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from cv import models, serializers
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
import photograph


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
