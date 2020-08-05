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
    A directory from the original image filesystem. Photographs must have one direct parent directory, which may itself have parent directories.
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
    """
    A job from the original archival description. Photographs may be associated with one job.
    """

    job_code = models.CharField(
        blank=True,
        unique=True,
        max_length=20,
        help_text="custom code used for this job",
    )
    date_start = models.DateField(help_text="Earliest date of this job")
    date_end = models.DateField(help_text="Latest date of this job")

