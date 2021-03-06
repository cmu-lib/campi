from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
import photograph
import cv
import campi


class Tag(campi.models.uniqueLabledModel):
    """
    Dictionary of content tags devised by editors
    """

    class Meta:
        ordering = ["label"]


class TaggingTask(campi.models.dateCreatedModel):
    """
    Tasks are defined as a combination of tag and CV model, and may have an assiged user
    """
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
        """
        If this task has a user, null out assigned users on other tasks
        """
        if self.assigned_user is not None:
            TaggingTask.objects.exclude(id=self.id).filter(
                assigned_user=self.assigned_user
            ).update(assigned_user=None)
        res = super().save(*args, **kwargs)
        return res


class TaggingDecision(campi.models.dateCreatedModel, campi.models.userCreatedModel):
    """
    Log whether an editor has explicitly approved or explicitly rejected a given tag for a photograph. This model keeps a log of decisions, while the PhotographTag model tracks the most recent state of tags for a photograph.
    """
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
        # Create and update tagging decisions for all photographs related
        other_photos = self.photograph.get_close_matches()
        if bool(other_photos):
            new_matches = other_photos.exclude(decisions__task=self.task)
            related_decisions = [
                TaggingDecision(
                    photograph=p,
                    task=self.task,
                    is_applicable=self.is_applicable,
                    user_created=self.user_created,
                )
                for p in new_matches
            ]
            TaggingDecision.objects.bulk_create(
                related_decisions, ignore_conflicts=True
            )
            updated_matches = TaggingDecision.objects.filter(
                task=self.task, photograph__in=other_photos
            )
            for m in updated_matches:
                m.is_applicable = self.is_applicable
                m.user_created = self.user_created
            TaggingDecision.objects.bulk_update(
                updated_matches, fields=["is_applicable", "user_created"]
            )

        # Create or update PhotographTag relationship if the editor decided the tag was applicable
        if self.is_applicable:
            pt = PhotographTag.objects.get_or_create(
                photograph=self.photograph, tag=self.task.tag
            )[0]
            pt.user_last_modified = self.user_created
            pt.last_update = timezone.now()
            pt.save()
        else:
            # If editor has decided it isn't applicable, remove any existing tag relationships
            to_be_removed = PhotographTag.objects.filter(
                photograph=self.photograph, tag=self.task.tag
            ).all()
            for pt in to_be_removed:
                pt.delete()
        res = super().save(*args, **kwargs)
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

    def save(self, *args, **kwargs):
        """
        Any photos in a close match set with this one also get tagged
        """
        other_photos = self.photograph.get_close_matches()
        if bool(other_photos):
            new_photo_tags = [
                PhotographTag(
                    photograph=p,
                    tag=self.tag,
                    last_updated=timezone.now(),
                    user_last_modified=self.user_last_modified,
                )
                for p in other_photos
            ]
            PhotographTag.objects.bulk_create(new_photo_tags, ignore_conflicts=True)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Any photos in a close match set with this one also get untagged
        """
        other_photos = self.photograph.get_close_matches()
        if bool(other_photos):
            PhotographTag.objects.filter(
                photograph__in=other_photos, tag=self.tag
            ).delete()
        super().delete(*args, **kwargs)
