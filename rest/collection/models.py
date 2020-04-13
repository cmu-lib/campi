from django.db import models
from django.conf import settings
from photograph import models as photograph_models
from campi.models import (
    labeledModel,
    uniqueLabledModel,
    descriptionModel,
    sequentialModel,
)

"""
Abstract models
"""


"""
Materialized models
"""


class Collection(uniqueLabledModel):
    # Optional parent collection model
    parent_collection = models.ForeignKey(
        "Collection",
        null=True,
        on_delete=models.CASCADE,
        related_name="child_collections",
    )
