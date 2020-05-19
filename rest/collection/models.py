from django.db import models
from django.conf import settings
import photograph
import campi


class Collection(campi.models.labeledModel):
    """
    A generic recursive collection model
    """

    parent_collection = models.ForeignKey(
        "Collection",
        null=True,
        on_delete=models.CASCADE,
        related_name="child_collections",
        help_text="The immediate parent of this collection",
    )


class Job(campi.models.labeledModel, campi.models.descriptionModel):
    date_start = models.DateField()
    date_end = models.DateField()
