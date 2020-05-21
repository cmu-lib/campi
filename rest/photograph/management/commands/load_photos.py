from django.core.management.base import BaseCommand
import photograph.models
import collection.models
import pytz
from tqdm import tqdm
from glob import glob
import datetime
import json
import re
from os.path import basename


class Command(BaseCommand):
    help = "Load photos into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe", action="store_true", help="Wipe all images before loading"
        )
        parser.add_argument("manifest", nargs="+", type=str)

    def get_immediate_directory(self, dir_paths):
        dir_paths.reverse()
        topdir_label = dir_paths.pop()
        topdir = collection.models.Directory.objects.get_or_create(label=topdir_label)[
            0
        ]

        if len(dir_paths) > 0:
            return self.make_next_child(topdir, dir_paths)
        else:
            return topdir

    def make_next_child(self, parent_dir, remaining_paths):
        next_path = remaining_paths.pop()
        next_dir = collection.models.Directory.objects.get_or_create(
            label=next_path, parent_directory=parent_dir
        )[0]
        if len(remaining_paths) > 0:
            return self.make_next_child(next_dir, remaining_paths)
        else:
            return next_dir

    def handle(self, *args, **options):
        manifest = json.load(open(options["manifest"][0], "r"))
        for item in tqdm(manifest):
            split_path = item["new"].split("/")[:-1]
            photo_directory = self.get_immediate_directory(split_path)
            year_match = re.match(r"^.+\D((19|20)\d{2})\D", item["new"])
            if year_match:
                start_year = int(year_match.groups()[0])
                end_year = start_year
                date_match = re.match(r"^.+/(\d{2})(\d{2})(\d{2})_", item["new"])
                if date_match:
                    start_month = int(date_match.groups()[1])
                    start_day = int(date_match.groups()[2])
                    end_month = start_month
                    end_day = start_day
                else:
                    start_month = 1
                    start_day = 1
                    end_month = 12
                    end_day = 31
            else:
                start_year = 1900
                end_year = 2020
                start_month = 1
                start_day = 1
                end_month = 12
                end_day = 31

            try:
                start_date = datetime.date(start_year, start_month, start_day)
            except:
                start_date = datetime.date(start_year, 1, 1)

            try:
                end_date = datetime.date(end_year, end_month, end_day)
            except:
                end_date = datetime.date(end_year, 12, 31)

            newimage = photograph.models.Photograph(
                label=basename(item["new"]),
                original_server_path=item["original"],
                image_path=item["new"].replace("TIF", "tif"),
                date_taken_early=start_date,
                date_taken_late=end_date,
                digitized_date=datetime.datetime.fromtimestamp(
                    item["created_date"], tz=pytz.UTC
                ),
                directory=photo_directory,
            )
            newimage.save()
