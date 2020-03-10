from django.db import models
from django.conf import settings
from photograph import models as photograph_models
from argus.models import labeledModel, descriptionModel, sequentialModel

"""
Abstract models
"""


"""
Materialized models
"""


class Collection(labeledModel):
    # Optional parent collection model
    parent_collection = models.ForeignKey(
        "Collection", null=True, on_delete=models.CASCADE
    )
