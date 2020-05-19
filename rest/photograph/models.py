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
        collection.models.Collection,
        related_name="immediate_photographs",
        on_delete=models.CASCADE,
        help_text="Parent directory",
    )
    all_directories = models.ManyToManyField(
        collection.models.Collection,
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

    def push_parent_directory(self, coll_instance):
        self.all_directories.add(coll_instance)
        instance_parent = coll_instance.parent_collection
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


class Annotation(campi.models.dateModifiedModel):
    photograph = models.ForeignKey(
        Photograph, on_delete=models.CASCADE, related_name="annotations"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="annotations"
    )
    x_min = models.PositiveIntegerField()
    x_max = models.PositiveIntegerField()
    y_max = models.PositiveIntegerField()
    y_max = models.PositiveIntegerField()

    @property
    def width(self):
        return self.x_max - self.x_min

    @property
    def height(self):
        return self.y_max - self.y_max

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
            render_stirng = f"{rw},{rh}"

        return f"{selfphotograph.iiif_base}/{self.x_min},{self.width},{self.y_max},{self.height}/{render_string}/0/default.jpg"
