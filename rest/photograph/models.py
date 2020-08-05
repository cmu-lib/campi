from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import campi.models
import collection.models
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import GinIndex


class Photograph(
    campi.models.labeledModel, campi.models.descriptionModel, campi.models.IIIFModel
):
    """
    A single photograph
    """

    original_server_path = models.CharField(
        max_length=2000,
        unique=True,
        editable=False,
        help_text="The original path and filename from the archives server",
    )
    date_taken_early = models.DateField(
        db_index=True,
        help_text="Earliest possible date the original photograph was taken",
    )
    date_taken_late = models.DateField(
        db_index=True,
        help_text="Latest possible date the original photograph was taken",
    )
    digitized_date = models.DateTimeField(
        db_index=True,
        help_text="Creation date of the original TIF file on the archives server",
    )
    directory = models.ForeignKey(
        collection.models.Directory,
        related_name="immediate_photographs",
        on_delete=models.CASCADE,
        help_text="Parent directory",
    )
    all_directories = models.ManyToManyField(
        collection.models.Directory,
        related_name="all_photographs",
        help_text="All ancestor directories. Provided for faster filtering.",
    )
    job = models.ForeignKey(
        collection.models.Job,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="photographs",
        help_text="Official CMU photographer job listing where this photograph was taken",
    )
    job_sequence = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Sequence in the series of photos taken during the job listing",
    )
    image_text = models.TextField(
        null=True,
        blank=False,
        default="",
        help_text="Any text recognized in the image by Google Cloud Vision",
    )
    image_search_text = SearchVectorField(
        null=True,
        editable=False,
        help_text="The GIN index field in postgres for the image_text field, allowing for simplistic full text search of recognized text in photographs.",
    )

    class Meta:
        ordering = ["image_path"]
        indexes = [GinIndex(fields=["image_search_text"])]

    def push_parent_directory(self, coll_instance):
        """
        Recursively add all the ancestor directories of this photograph to the all_directories m2m field
        """
        self.all_directories.add(coll_instance)
        instance_parent = coll_instance.parent_directory
        if instance_parent is not None:
            self.push_parent_directory(instance_parent)
        else:
            return

    def add_all_parent_directories(self):
        self.push_parent_directory(self.directory)

    def save(self, *args, **kwargs):
        """
        On save, update parent directories and update the text index on the image_text field
        """
        response = super().save(*args, **kwargs)
        self.add_all_parent_directories()
        Photograph.objects.filter(id=self.id).update(
            image_search_text=SearchVector("image_text")
        )
        return response

    def get_close_matches(self):
        """
        A helper function used in some views that returns the other photographs belonging to the same close match set as this photograph.
        """
        match_membership = self.close_match_memberships.filter(state="a")

        other_photos = (
            Photograph.objects.filter(
                close_match_memberships__close_match_set__memberships__in=match_membership,
                close_match_memberships__state="a",
            )
            .exclude(id=self.id)
            .distinct()
        )
        return other_photos


class Annotation(models.Model):
    """
    Abstract class for any annotation on a photograph that is connected to a specific bounding box. Provides fields and functions to calculate a IIIF request URL for the annotated image region.
    """

    photograph = models.ForeignKey(
        Photograph, on_delete=models.CASCADE, related_name="%(class)s"
    )
    x = models.PositiveIntegerField(
        help_text="Number of pixels from the left side of the image"
    )
    width = models.PositiveIntegerField(help_text="Width of the region in pixes")
    y = models.PositiveIntegerField(
        help_text="Number of pixels from the top side of the image"
    )
    height = models.PositiveIntegerField(help_text="Height of the region in pixes")

    @property
    def x_max(self):
        return self.x + self.width

    @property
    def y_max(self):
        return self.y + self.height

    def image(self, rendered_width=None, rendered_height=None):
        if rendered_width is None:
            rw = ""
        else:
            rw = rendered_width

        if rendered_height is None:
            rh = ""
        else:
            rh = rendered_height

        if rendered_width is None and rendered_height is None:
            render_string = "full"
        else:
            render_string = f"!{rw},{rh}"

        return f"{self.photograph.iiif_base}/{self.x},{self.y},{self.width},{self.height}/{render_string}/0/default.jpg"

    @property
    def thumbnail(self):
        return self.image(rendered_height=300, rendered_width=300)

    class Meta:
        abstract = True


class FaceAnnotation(Annotation):
    """
    Google Cloud VisionAPI face recognition annotation metadata (https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse#faceannotation)
    """

    detection_confidence = models.FloatField(null=True, db_index=True)
    joy_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    sorrow_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    anger_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    surprise_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    under_exposed_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    blurred_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    headwear_likelihood = models.PositiveIntegerField(null=True, db_index=True)


class ObjectAnnotationLabel(campi.models.uniqueLabledModel):
    """
    A unique dictionary of object labels found in the Google Cloud Vision API object localization responses
    """

    pass


class ObjectAnnotation(Annotation):
    """
    Google Cloud Vision API object localization (https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse#localizedobjectannotation)
    """

    label = models.ForeignKey(
        ObjectAnnotationLabel, on_delete=models.CASCADE, related_name="annotations"
    )
    score = models.FloatField()


class PhotoLabel(campi.models.uniqueLabledModel):
    """
    A unique dictionary of labels found in the Google Cloud Vision API label annotations
    """

    pass


class PhotoLabelAnnotation(models.Model):
    """
    Google Cloud Vision API label annotations
    """

    photograph = models.ForeignKey(
        Photograph, on_delete=models.CASCADE, related_name="label_annotations"
    )
    label = models.ForeignKey(
        PhotoLabel, on_delete=models.CASCADE, related_name="annotations"
    )
    score = models.FloatField(db_index=True)


class TextAnnotation(
    Annotation, campi.models.labeledModel, campi.models.sequentialModel
):
    """
    Google Cloud Vision API's text recognition response isolates multiple bounding boxes with text strings per image. We store those in this model. The concatenated text used for full text indexing is stored in the Photograph's image_text field.
    """

    class Meta:
        unique_together = ("photograph", "sequence")
