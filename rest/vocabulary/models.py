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


class Person(labeledModel, descriptionModel):
    first_name = models.CharField(null=True, blank=True, max_length=800)
    last_name = models.CharField(null=True, blank=True, max_length=800, db_index=True)


class Tag(labeledModel):
    parent = models.ForeignKey(
        "Tag", null=True, on_delete=models.CASCADE, related_name="children"
    )
