from django import forms
from django.db.models import Count, Q, Prefetch
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from tagging import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
import photograph


class TagFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="tags with this text in their label", lookup_expr="icontains"
    )


class TagViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    tagging_tasks = models.TaggingTask.objects.prefetch_related(
        "assigned_user", "pytorch_model", "tag"
    )
    queryset = (
        models.Tag.objects.annotate(n_images=Count("photograph_tags", distinct=True))
        .prefetch_related(Prefetch("tasks", queryset=tagging_tasks))
        .all()
    )
    serializer_class = serializers.TagSerializer
    filterset_class = TagFilter
    ordering = ["label", "n_images"]


class TaggingTaskViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.TaggingTask.objects.prefetch_related(
        "assigned_user", "pytorch_model", "tag"
    )
    serializer_class = serializers.TaggingTaskSerializer
    serializer_action_classes = {
        "list": serializers.TaggingTaskSerializer,
        "detail": serializers.TaggingTaskSerializer,
        "create": serializers.TaggingTaskPostSerializer,
        "update": serializers.TaggingTaskPostSerializer,
        "partial_update": serializers.TaggingTaskPostSerializer,
    }

    @action(detail=True, methods=["get"], name="Get the next set of nearest neighbors")
    def get_nn(self, request, pk=None):
        task = self.get_object()
        photo_id = int(request.query_params["photograph"])
        n_neighbors = int(request.query_params["n_neighbors"])
        try:
            seed_photo = photograph.models.Photograph.objects.get(id=photo_id)
        except:
            return Response(
                {"error": f"No photograph exists with the id {photo_id}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            # Has this task started yet?
        if task.decisions.exists():
            untagged_photos = photograph.models.Photograph.objects.exclude(
                decisions__task=task
            ).exclude(photograph_tags__tag=task.tag)

            tasked_photos = photograph.models.Photograph.objects.filter(
                decisions__in=task.decisions.filter(is_applicable=True)
            )

            composite_vector = task.pytorch_model.get_summed_vector(tasked_photos)

            nn = task.pytorch_model.get_arbitrary_nn(
                composite_vector,
                photo_queryset=untagged_photos,
                n_neighbors=n_neighbors,
            )
        else:
            nn = task.pytorch_model.get_nn(seed_photo, n_neighbors=n_neighbors)
        serialized_neighbors = photograph.serializers.PhotographDistanceListSerializer(
            photograph.views.prepare_photograph_qs(nn),
            many=True,
            context={"request": request},
        ).data
        return Response(serialized_neighbors, status.HTTP_200_OK)


class TaggingDecisionViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.TaggingDecision.objects.all()
    serializer_class = serializers.TaggingDecisionSerializer


class PhotographTagViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.PhotographTag.objects.all()
    serializer_class = serializers.PhotographTagPostSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        photograph_tag_serializer = self.get_serializer_class()(data=request.data)
        if photograph_tag_serializer.is_valid():
            obj = photograph_tag_serializer.save()
            obj.user_last_edited = request.user
            obj.save()
            return Response(None, status=status.HTTP_201_CREATED)
        else:
            return Response(
                photograph_tag_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

