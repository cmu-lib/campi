from django.db import models
from django.contrib.postgres.fields import JSONField
import photograph


class GCVResponse(models.Model):
    photograph = models.OneToOneField(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="gcv_response",
        help_text="Source photograph for this response",
    )
    json = JSONField()
