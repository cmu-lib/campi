from django.db import models

"""
Abstract models
"""


class labeledModel(models.Model):
    label = models.CharField(null=False, blank=True, max_length=1000, default="")

    class Meta:
        abstract = True

    def __str__(self):
        return self.label


class uniqueLabledModel(labeledModel):
    label = models.CharField(null=False, blank=False, max_length=1000, unique=True)

    class Meta:
        abstract = True


class descriptionModel(models.Model):
    description = models.TextField(null=False, blank=True, max_length=10000)

    class Meta:
        abstract = True


class sequentialModel(labeledModel):
    sequence = models.PositiveIntegerField(db_index=True)

    class Meta:
        abstract = True
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.label} - {self.sequence}"
