from django.http import HttpResponse
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
import csv


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

    directory = filters.ModelChoiceFilter(
        queryset=collection.models.Directory.objects.all(), method="by_directory"
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

    gcv_object = filters.ModelChoiceFilter(
        queryset=photograph.models.ObjectAnnotationLabel.objects.all(),
        method="by_gcv_object",
    )

    def by_gcv_object(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    photograph.models.ObjectAnnotationLabel.objects.filter(
                        id=value.id,
                        annotations__photograph__photograph_tags__tag=OuterRef("pk"),
                    )
                )
            )

    gcv_label = filters.ModelChoiceFilter(
        queryset=photograph.models.PhotoLabel.objects.all(), method="by_gcv_label"
    )

    def by_gcv_label(self, queryset, name, value):
        if value is None:
            return queryset
        else:
            return queryset.filter(
                Exists(
                    photograph.models.PhotoLabel.objects.filter(
                        id=value.id,
                        annotations__photograph__photograph_tags__tag=OuterRef("pk"),
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
                status=status.HTTP_403_FORBIDDEN,
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

            photo_vector = task.pytorch_model.get_photo_embeddings(photo_id)

            nn = task.pytorch_model.get_arbitrary_nn(
                photo_vector, photo_queryset=untagged_photos, n_neighbors=n_neighbors,
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

    @action(detail=False, methods=["get"])
    def download_all_tags(
        self, request, name="Download a CSV with all photo-tag combinations",
    ):

        all_photo_tags = (
            self.queryset.select_related("photograph", "tag", "user_last_modified")
            .order_by("photograph_id")
            .values(
                "photograph_id",
                "photograph__original_server_path",
                "tag_id",
                "tag__label",
                "user_last_modified__username",
                "last_updated",
            )
        )
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=photograph_tags.csv"
        writer = csv.writer(response)
        headers = [
            "photograph_id",
            "photograph_file_name",
            "tag_id",
            "tag_label",
            "tagging_user",
            "date_tagged",
        ]
        writer.writerow(headers)
        for pt in all_photo_tags:
            writer.writerow(
                [
                    pt["photograph_id"],
                    pt["photograph__original_server_path"],
                    pt["tag_id"],
                    pt["tag__label"],
                    pt["user_last_modified__username"],
                    pt["last_updated"],
                ]
            )

        return response
