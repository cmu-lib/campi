from django.db import models
from django.contrib.postgres.fields import JSONField
import photograph
from campi.models import dateModifiedModel


class GCVResponse(dateModifiedModel):
    photograph = models.OneToOneField(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="gcv_response",
        help_text="Source photograph for this response",
    )
    json = JSONField()
