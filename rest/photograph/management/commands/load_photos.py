from django.core.management.base import BaseCommand
from photograph import models
from metadata.models import Collection
from tqdm import tqdm
from glob import glob
import datetime
import re
import os


class Command(BaseCommand):
    help = "Load photos into the database"

    def add_arguments(self, parser):
        parser.add_argument("folder", nargs="+", type=str)
        parser.add_argument(
            "--wipe", action="store_true", help="Wipe all boxes before loading"
        )
        parser.add_argument(
            "--year",
            action="store_true",
            help="Year to assign to photographs",
            type=int,
        )

    def handle(self, *args, **options):
        assigned_year = options["year"]
        if options["wipe"]:
            models.Photographs.objects.filter(date_early__).delete()
        box_path = options["box_path"][0]
        collection = Collection.objects.get_or_create(label=box_path)[0]

        imagefiles = glob(box_path + "*.jp2")

        for image_path in imagefiles:
            print(image_path)
            newimage = models.Photograph.objects.create(
                image_path=image_path,
                date_early=datetime.date(options["year"], 1, 1),
                date_late = datetime.date(options["year"], 12, 31),
                digitzed_date = datetime.date.now()
                collection = collection
            )
