from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from os.path import basename

"""
Abstract models used across the rest of the application
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

    def __str__(self):
        return self.label


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


class dateCreatedModel(models.Model):
    created_on = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True,
        help_text="Date created (automatically recorded)",
    )

    class Meta:
        abstract = True


class dateModifiedModel(dateCreatedModel):
    last_updated = models.DateTimeField(
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
    Provides a fields for storing a root IIIF image path, the full height and width in pixels, as well as several useful calculated properties such as thumbnail image, square, etc.
    """

    image_path = models.CharField(
        max_length=2000,
        unique=True,
        editable=False,
        help_text="Base path for the image on the IIIF server",
        db_index=True,
    )
    height = models.PositiveIntegerField(
        default=0, help_text="The height of the original image in pixels"
    )
    width = models.PositiveIntegerField(
        default=0, help_text="The width of the original image in pixels"
    )

    @property
    def filename(self):
        return basename(self.image_path)

    @property
    def iiif_base(self):
        """
        settings.IMAGE_BASURL can be configured to match the specific location of the outside IIIF server.
        """
        return f"{settings.IMAGE_BASEURL}{self.image_path}".replace("&", "%26")
        # We used IIPImage server as our IIIF source, and due to an oversight when loading original images, we failed ot remove a few special characters. To manage the difference btween what IIPImage Server expected and what we had already stored in our data, we added this hacky replace() to URLencode ampersands.

    @property
    def iiif_info(self):
        return f"{self.iiif_base}/info.json"

    @property
    def full_image(self):
        return f"{self.iiif_base}/full/full/0/default.jpg"

    @property
    def thumbnail_image(self):
        return f"{self.iiif_base}/full/600,/0/default.jpg"

    @property
    def square_thumbnail_image(self):
        return f"{self.iiif_base}/square/230,/0/default.jpg"

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
