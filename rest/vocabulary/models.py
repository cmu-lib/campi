from django.db import models
from django.conf import settings
import campi.models


class Person(campi.models.descriptionModel):
    first_name = models.CharField(null=True, blank=True, max_length=800)
    last_name = models.CharField(null=True, blank=True, max_length=800, db_index=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Tag(campi.models.labeledModel):
    parent = models.ForeignKey(
        "Tag", null=True, on_delete=models.CASCADE, related_name="children"
    )
