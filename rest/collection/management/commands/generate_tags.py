from django.core.management.base import BaseCommand
from django.db.models import F
import collection.models
from tqdm import tqdm
import re


class Command(BaseCommand):
    help = "Generate jobtags from job labels"

    def handle(self, *args, **options):
        # wipe existing jobtags
        collection.models.JobTag.objects.all().delete()

        all_labels = (
            collection.models.Job.objects.exclude(label=F("job_code"))
            .exclude(label="")
            .all()
        )
        for j in tqdm(all_labels):
            multi_tags = [s.lower().strip() for s in re.split(r"[,-/;]", j.label)]
            for t in multi_tags:
                if t != "" and len(t) > 1:
                    tag = collection.models.JobTag.objects.get_or_create(label=t)[0]
                    j.tags.add(tag)
