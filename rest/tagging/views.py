from django import forms
from django.db.models import Count, Q, Prefetch, Exists, OuterRef
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from tagging import serializers, models
from django_filters import rest_framework as filters
from campi.views import GetSerializerClassMixin
import photograph
import collection


class TagFilter(filters.FilterSet):
    label = filters.CharFilter(
        help_text="tags with this text in their label", lookup_expr="icontains"
    )
    job = filters.ModelChoiceFilter(
        queryset=collection.models.Job.objects.all(), method="by_job"
    )

    def by_job(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    collection.models.Job.objects.filter(
                        id=value.id, photographs__photograph_tags__tag=OuterRef("pk")
                    )
                )
            )

    job_tag = filters.ModelChoiceFilter(
        queryset=collection.models.JobTag.objects.all(), method="by_job_tag"
    )

    def by_job_tag(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    collection.models.JobTag.objects.filter(
                        id=value.id,
                        jobs__photographs__photograph_tags__tag=OuterRef("pk"),
                    )
                )
            )

    directory = filters.ModelChoiceFilter(
        queryset=collection.models.Directory.objects.all(),
        field_name="photograph_tags__photograph__directory",
    )

    def by_directory(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    collection.models.Directory.objects.filter(
                        id=value.id,
                        immediate_photographs__photograph_tags__tag=OuterRef("pk"),
                    )
                )
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
    queryset = models.TaggingTask.objects.select_related(
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

    @action(detail=True, methods=["post"], name="Check a tag back in")
    def check_in(self, request, pk=None):
        task = self.get_object()
        if task.assigned_user == request.user:
            task.assigned_user = None
            task.save()
            return Response(
                {"success": "Tag checked back in"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "error": "Requesting user does not match the currently assigned user."
                },
                error=status.HTTP_403_FORBIDDEN,
            )

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

            rejected_photos = photograph.models.Photograph.objects.filter(
                decisions__in=task.decisions.filter(is_applicable=False)
            )

            if tasked_photos.exists():
                # If there have been any approved photos, create a new vector from their embeddings
                composite_vector = task.pytorch_model.get_weighted_vector(
                    tasked_photos, photo_id
                )
            else:
                # If none of the reviewed photos have yet been accepted, then stick to the original seed photo vector
                composite_vector = task.pytorch_model.get_photo_embeddings(photo_id)

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


class TaggingDecisionFilterset(filters.FilterSet):
    task = filters.ModelChoiceFilter(queryset=models.TaggingTask.objects.all())
    photograph = filters.ModelChoiceFilter(
        queryset=photograph.models.Photograph.objects.all()
    )


class TaggingDecisionViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.TaggingDecision.objects.all()
    serializer_class = serializers.TaggingDecisionSerializer
    filterset_class = TaggingDecisionFilterset


class PhotographTagViewset(GetSerializerClassMixin, viewsets.ModelViewSet):
    queryset = models.PhotographTag.objects.all()
    serializer_class = serializers.PhotographTagPostSerializer
