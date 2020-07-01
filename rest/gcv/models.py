from django.db import models
from picklefield.fields import PickledObjectField
import photograph
from campi.models import dateCreatedModel


class GCVResponse(dateCreatedModel):
    photograph = models.OneToOneField(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="gcv_response",
        help_text="Source photograph for this response",
    )
    annotations = PickledObjectField(null=True)
