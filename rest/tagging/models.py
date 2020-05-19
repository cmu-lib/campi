from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import photograph
import campi


class Task(campi.models.descriptionModel, campi.models.dateModifiedModel):
    pass


class Action(campi.models.dateModifiedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tagging_actions",
        help_text="User who carried out this action",
    )

