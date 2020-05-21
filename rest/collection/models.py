from django.db import models
from django.conf import settings
from django.urls import reverse
import photograph
import campi


class Directory(
    campi.models.labeledModel,
    campi.models.descriptionModel,
    campi.models.userModifiedModel,
):
    """
    A directory from the original image filesystem
    """

    parent_directory = models.ForeignKey(
        "Directory",
        null=True,
        on_delete=models.CASCADE,
        related_name="child_directories",
        help_text="The immediate parent of this directory",
    )


class Job(
    campi.models.labeledModel,
    campi.models.descriptionModel,
    campi.models.userModifiedModel,
):
    date_start = models.DateField()
    date_end = models.DateField()
