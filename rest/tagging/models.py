from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import photograph
import cv
import campi


class Tag(campi.models.uniqueLabledModel):
    def merge(self, child_tag):
        affected_tasks = (
            tagging.models.TaggingTask.objects.filter(applied_term=child_tag)
            .exclude(applied_term=self)
            .all()
        )

        for t in affected_tasks:
            t.applied_term = self

        res = tagging.models.TaggingTask.objects.bulk_update(
            affected_tasks, ["applied_term"]
        )

        return res

    class Meta:
        ordering = ["label"]


class TaggingTask(campi.models.descriptionModel, campi.models.dateModifiedModel):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tagging_tasks",
        help_text="The vocabulary tag to be applied when working this task",
    )
    pytorch_model = models.ForeignKey(
        cv.models.PyTorchModel,
        on_delete=models.CASCADE,
        related_name="tagging_tasks",
        help_text="The CV model associated with this tagging task",
    )
    assigned_user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="active_tags",
        help_text="The user currently working on this tagging task",
    )

    class Meta:
        unique_together = ("tag", "pytorch_model")


class TaggingDecision(campi.models.dateModifiedModel, campi.models.userCreatedModel):
    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="tagging_decisions",
        help_text="The photograph this tagging decision applies to",
    )
    task = models.ForeignKey(
        TaggingTask, on_delete=models.CASCADE, related_name="tagging_decisions"
    )
    is_applicable = models.NullBooleanField(
        null=True,
        default=None,
        db_index=True,
        help_text="Is the given tag applicable to this photograph?",
    )

    class Meta:
        unique_together = ("photograph", "task")

