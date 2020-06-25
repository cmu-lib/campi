from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
import photograph
import cv
import campi


class Tag(campi.models.uniqueLabledModel):
    def merge(self, child_tag):
        affected_tasks = (
            tagging.models.TaggingTask.objects.filter(tag=child_tag)
            .exclude(applied_term=self)
            .all()
        )

        for t in affected_tasks:
            t.applied_term = self

        res = tagging.models.TaggingTask.objects.bulk_update(affected_tasks, ["tag"])

        return res

    class Meta:
        ordering = ["label"]


class TaggingTask(campi.models.dateCreatedModel):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="The vocabulary tag to be applied when working this task",
    )
    pytorch_model = models.ForeignKey(
        cv.models.PyTorchModel,
        on_delete=models.CASCADE,
        related_name="tasks",
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

    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)
        # If this task has a user, null out assigned users on other tasks
        if self.assigned_user is not None:
            TaggingTask.objects.exclude(id=self.id).filter(
                assigned_user=self.assigned_user
            ).update(assigned_user=None)
        return res


class TaggingDecision(campi.models.dateCreatedModel, campi.models.userCreatedModel):
    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="decisions",
        help_text="The photograph this tagging decision applies to",
    )
    task = models.ForeignKey(
        TaggingTask, on_delete=models.CASCADE, related_name="decisions"
    )
    is_applicable = models.NullBooleanField(
        null=True,
        default=None,
        db_index=True,
        help_text="Is the given tag applicable to this photograph?",
    )

    class Meta:
        unique_together = ("photograph", "task")

    @transaction.atomic
    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)
        # Create or update PhotographTag relationship if the editor decided the tag was applicable
        if self.is_applicable:
            PhotographTag.objects.update_or_create(
                photograph=self.photograph,
                tag=self.task,
                defaults={
                    "user_last_modified": self.user_created,
                    "last_updated": timezone.now(),
                },
            )
        else:
            # If editor has decided it isn't applicable, remove any existing tag relationships
            PhotographTag.objects.filter(
                photograph=self.photograph, tag=self.task
            ).all().delete()
        return res


class PhotographTag(campi.models.dateModifiedModel, campi.models.userModifiedModel):
    """
    This through model will be the authoritative photograph/tag relationship through table, which allows tags to be added both through the dedicated TaggingTask/TaggingDecision workflows, as well as with arbitrary POST commands as needed.
    """

    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="photograph_tags",
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="photograph_tags"
    )

    class Meta:
        unique_together = ("photograph", "tag")
