from django.db import models
from django.conf import settings

"""
Abstract models
"""


class labeledModel(models.Model):
    label = models.CharField(null=False, blank=True, max_length=1000, default="")

    class Meta:
        abstract = True

    def __str__(self):
        if self.label is None:
            return "%(class)s " + self.id
        else:
            return self.label


class uniqueLabledModel(labeledModel):
    label = models.CharField(null=False, blank=False, max_length=1000, unique=True)

    class Meta:
        abstract = True


class descriptionModel(models.Model):
    description = models.TextField(null=False, blank=True, max_length=10000)

    class Meta:
        abstract = True


class sequentialModel(models.Model):
    sequence = models.PositiveIntegerField(db_index=True)

    class Meta:
        abstract = True
        ordering = ["sequence"]


class dateModifiedModel(models.Model):
    created_on = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True,
        help_text="Date created (automatically recorded)",
    )
    last_updated = models.DateField(
        auto_now=True,
        editable=False,
        db_index=True,
        help_text="Date last modified (automatically recorded)",
    )

    class Meta:
        abstract = True


class IIIFModel(models.Model):
    image_path = models.CharField(
        max_length=2000,
        unique=True,
        editable=False,
        help_text="Base path for the image on the IIIF server",
    )

    @property
    def iiif_base(self):
        return settings.IMAGE_BASEURL + self.image_path.replace("#", "%23")

    @property
    def iiif_info(self):
        return f"{self.iiif_base}/info.json"

    @property
    def full_image(self):
        return f"{self.iiif_base}/full/full/0/default.jpg"

    @property
    def thumbnail_image(self):
        return f"{self.iiif_base}/full/400,/0/default.jpg"

    @property
    def square_thumbnail_image(self):
        return f"{self.iiif_base}/square/150,/0/default.jpg"

    @property
    def image(self):
        return {
            "id": self.iiif_base,
            "info": self.iiif_info,
            "full": self.full_image,
            "thumbnail": self.thumbnail_image,
            "square": self.square_thumbnail_image,
        }

    class Meta:
        abstract = True
