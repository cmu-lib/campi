from django.db import models
from django.conf import settings
from django.urls import reverse
import photograph
import campi


class Directory(
    campi.models.labeledModel,
    campi.models.descriptionModel,
    campi.models.userModifiedModel,
):
    """
    A directory from the original image filesystem
    """

    parent_directory = models.ForeignKey(
        "Directory",
        null=True,
        on_delete=models.CASCADE,
        related_name="child_directories",
        help_text="The immediate parent of this directory",
    )


class Job(
    campi.models.labeledModel,
    campi.models.descriptionModel,
    campi.models.userModifiedModel,
):
    job_code = models.CharField(
        blank=True,
        unique=True,
        max_length=20,
        help_text="custom code used for this job",
    )
    date_start = models.DateField(help_text="Earliest date of this job")
    date_end = models.DateField(help_text="Latest date of this job")
    tags = models.ManyToManyField(
        "JobTag",
        related_name="jobs",
        through="JobsTags",
        through_fields=("job", "job_tag"),
        help_text="Tags for this job",
    )


class JobTag(
    campi.models.uniqueLabledModel,
    campi.models.descriptionModel,
    campi.models.userModifiedModel,
):
    def merge(self, target):
        """
        Merge the target tag into this tag
        """

        affected_jobs = JobsTags.objects.filter(job_tag=target)
        jobs_with_this_tag = JobsTags.objects.filter(job_tag=self)
        # If jobs already have this tag, then only delete the target rels
        n_deleted = affected_jobs.filter(job__in=jobs_with_this_tag).delete()
        # All other jobs, update the job_tag to be this tag
        n_updated = affected_jobs.update(job_tag=self)
        # Finally, delete the target
        target.delete()

        return {"n_deleted": n_deleted, "n_updated": n_updated}


class JobsTags(models.Model):
    job = models.ForeignKey(Job, related_name="jobs_tags", on_delete=models.CASCADE)
    job_tag = models.ForeignKey(
        JobTag, related_name="jobs_tags", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("job", "job_tag")
