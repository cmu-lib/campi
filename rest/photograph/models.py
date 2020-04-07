from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from vocabulary import models as vocabulary_models
from collection import models as collection_models
from argus.models import labeledModel, descriptionModel, sequentialModel

"""
Materialized models
"""


class Photograph(labeledModel, descriptionModel):
    image_path = models.CharField(null=True, blank=False, max_length=800)
    date_early = models.DateField(db_index=True)
    date_late = models.DateField(db_index=True)
    digitized_date = models.DateField()
    taken_by = models.ForeignKey(
        vocabulary_models.Person,
        null=True,
        on_delete=models.CASCADE,
        related_name="photographs_taken",
    )
    depicts = models.ManyToManyField(vocabulary_models.Person)
    collection = models.ForeignKey(
        collection_models.Collection,
        related_name="photographs",
        on_delete=models.CASCADE,
    )

    def validate_collections(self):
        """
        If photograph belongs to a collection, ensure that it belongs to all parents of that collection too.
        """
        all_parents = set(
            [c.get_all_parent_collections() for c in self.collections.all()]
        )
        self.collections.add(all_parents)

    @property
    def iiif_base(self):
        return settings.IMAGE_BASEURL + self.image_path

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


class Annotation(models.Model):
    photograph = models.ForeignKey(
        Photograph, on_delete=models.CASCADE, related_name="annotations"
    )
    person_depicted = models.ForeignKey(
        vocabulary_models.Person, on_delete=models.CASCADE, related_name="annotations"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="annotations"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    x_min = models.IntegerField()
    x_max = models.IntegerField()
    y_max = models.IntegerField()
    y_max = models.IntegerField()

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
