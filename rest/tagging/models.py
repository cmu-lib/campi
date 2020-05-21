from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import photograph
import vocabulary
import cv
import campi


class Task(
    campi.models.descriptionModel,
    campi.models.dateModifiedModel,
    campi.models.userCreatedModel,
    campi.models.userModifiedModel,
):
    applied_term = models.ForeignKey(
        vocabulary.models.Tag,
        on_delete=models.CASCADE,
        related_name="tagging_tasks",
        help_text="The vocabulary tag to be applied when creating this task",
    )
    index = models.ForeignKey(
        cv.models.AnnoyIdx,
        on_delete=models.CASCADE,
        related_name="tags_made",
        help_text="The nearest neighbor index referenced while executing this task",
    )


class Decision(
    campi.models.dateModifiedModel,
    campi.models.userCreatedModel,
    campi.models.userModifiedModel,
):
    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="tagging_decisions",
        help_text="The photograph this tagging decision applies to",
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="tagging_decisions"
    )
    is_applicable = models.BooleanField(
        db_index=True, help_text="Is the given tag applicable to this photograph?"
    )
