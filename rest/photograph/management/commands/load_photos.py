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
        negatives = [
            n
            for n in manifest
            if "0000_62_General_Photograph_Collection/Negatives/" in n["new"]
        ]
        for item in tqdm(negatives):
            split_path = item["new"].split("/")[:-1]
            photo_directory = self.get_immediate_directory(split_path)
            year_match = re.match(r"^.+/((19|20)\d{2})\D", item["new"])
            if year_match:
                start_year = int(year_match.groups()[0])
                end_year = start_year
                short_jobcode = re.match(
                    r"^.+/(?:\w+_)?(\d{2})(\d{3}[A-Za-z]?)_", item["new"]
                )
                long_jobcode = re.match(
                    r"^.+/(?:\w+_)?(\d{2})(\d{2})(\d{2})_([A-Za-z0-9]+)[_\.]",
                    item["new"],
                )
                if long_jobcode:
                    start_month = int(long_jobcode.groups()[1])
                    start_day = int(long_jobcode.groups()[2])
                    end_month = start_month
                    end_day = start_day
                    job_code = f"{long_jobcode.groups()[0]}-{long_jobcode.groups()[1]}-{long_jobcode.groups()[2]}-{long_jobcode.groups()[3]}"
                elif short_jobcode:
                    start_month = 1
                    start_day = 1
                    end_month = 12
                    end_day = 31
                    job_code = (
                        f"{short_jobcode.groups()[0]}-{short_jobcode.groups()[1]}"
                    )
                else:
                    start_year = 1900
                    end_year = 2020
                    start_month = 1
                    start_day = 1
                    end_month = 12
                    end_day = 31
                    job_code = None
            else:
                start_year = 1900
                end_year = 2020
                start_month = 1
                start_day = 1
                end_month = 12
                end_day = 31
                job_code = None

            try:
                start_date = datetime.date(start_year, start_month, start_day)
            except:
                try:
                    start_date = datetime.date(start_year, start_month, start_day - 1)
                except:
                    try:
                        start_date = datetime.date(
                            start_year, start_month, start_day - 2
                        )
                    except:
                        start_date = datetime.date(start_year, 1, 1)

            try:
                end_date = datetime.date(end_year, end_month, end_day)
            except:
                try:
                    end_date = datetime.date(end_year, end_month, end_day - 1)
                except:
                    try:
                        end_date = datetime.date(end_year, end_month, end_day - 2)
                    except:
                        end_date = datetime.date(end_year, 1, 1)

            if job_code is not None:
                try:
                    job = collection.models.Job.objects.get_or_create(
                        job_code=job_code,
                        label=job_code,
                        date_start=start_date,
                        date_end=end_date,
                    )[0]
                except:
                    # In case the job exists with a different date already
                    job = collection.models.Job.objects.get(job_code=job_code)
            else:
                job = None

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
                job=job,
            )
            newimage.save()
