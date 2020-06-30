from django.core.management.base import BaseCommand
from cv.models import PyTorchModel
from glob import glob
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Delete any index files that don't have a corresponding database entry."

    def handle(self, *args, **options):
        # wipe existing jobtags
        matched_files = PyTorchModel.objects.all().values_list(
            "annoy_idx_file", flat=True
        )
        on_disk_files = glob(f"{settings.DIST_INDICES_PATH}/*.ix")

        for ifile in on_disk_files:
            if not ifile in matched_files:
                print(f"Removing {ifile}")
                os.remove(ifile)

