from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from os.path import basename

"""
Abstract models
"""


class labeledModel(models.Model):
    label = models.CharField(
        null=False,
        blank=True,
        max_length=400,
        default="",
        help_text="Short readable label",
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.label is None:
            return "%(class)s " + self.id
        else:
            return self.label


class uniqueLabledModel(labeledModel):
    label = models.CharField(
        null=False,
        blank=False,
        max_length=400,
        unique=True,
        help_text="Unique short readable label",
    )

    class Meta:
        abstract = True


class descriptionModel(models.Model):
    description = models.TextField(
        null=False, blank=True, help_text="Descriptive notes"
    )

    class Meta:
        abstract = True


class sequentialModel(models.Model):
    sequence = models.PositiveIntegerField(
        db_index=True, help_text="Sequence within a set"
    )

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


class userCreatedModel(models.Model):
    user_created = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        editable=False,
        null=True,
        related_name="%(class)ss_created",
        help_text="Created by user",
    )

    class Meta:
        abstract = True


class userModifiedModel(models.Model):
    user_last_modified = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        editable=False,
        null=True,
        related_name="%(class)ss_modified",
        help_text="Last modified by user",
    )

    class Meta:
        abstract = True


class IIIFModel(models.Model):
    """
    Provides a field for storing a root IIIF image path, as well as several useful calculated properties such as thumbnail image, square, etc.
    """

    image_path = models.CharField(
        max_length=2000,
        unique=True,
        editable=False,
        help_text="Base path for the image on the IIIF server",
    )

    @property
    def filename(self):
        return basename(self.image_path)

    @property
    def iiif_base(self):
        return f"{settings.IMAGE_BASEURL}{self.image_path}"

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
        """
        Useful default IIIF links for an image nested in a JSON object
        """
        return {
            "id": self.iiif_base,
            "info": self.iiif_info,
            "full": self.full_image,
            "thumbnail": self.thumbnail_image,
            "square": self.square_thumbnail_image,
        }

    class Meta:
        abstract = True
