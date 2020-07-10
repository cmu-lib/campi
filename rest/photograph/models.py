from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import campi.models
import collection.models


class Photograph(
    campi.models.labeledModel, campi.models.descriptionModel, campi.models.IIIFModel
):
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

    class Meta:
        ordering = ["image_path"]

    def push_parent_directory(self, coll_instance):
        self.all_directories.add(coll_instance)
        instance_parent = coll_instance.parent_directory
        if instance_parent is not None:
            self.push_parent_directory(instance_parent)
        else:
            return

    def add_all_parent_directories(self):
        self.push_parent_directory(self.directory)

    def save(self, *args, **kwargs):
        response = super().save(*args, **kwargs)
        self.add_all_parent_directories()
        return response

    def get_close_matches(self):
        if self.close_match_memberships.filter(state="a").exists():
            other_photo_ids = (
                self.close_match_memberships.filter(state="a")
                .first()
                .close_match_set.memberships.exclude(photograph=self)
                .all()
                .values_list("photograph__id", flat=True)
            )
            other_photos = Photograph.objects.filter(id__in=other_photo_ids)
            return other_photos
        else:
            return None


class Annotation(models.Model):
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
    detection_confidence = models.FloatField(null=True, db_index=True)
    joy_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    sorrow_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    anger_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    surprise_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    under_exposed_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    blurred_likelihood = models.PositiveIntegerField(null=True, db_index=True)
    headwear_likelihood = models.PositiveIntegerField(null=True, db_index=True)


class ObjectAnnotationLabel(campi.models.uniqueLabledModel):
    pass


class ObjectAnnotation(Annotation):
    label = models.ForeignKey(
        ObjectAnnotationLabel, on_delete=models.CASCADE, related_name="annotations"
    )
    score = models.FloatField()
