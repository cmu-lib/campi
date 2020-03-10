from django.core.management.base import BaseCommand
from photograph import models as photograph_models
from collection import models as collection_models
from tqdm import tqdm
from glob import glob
import datetime
import re
import os


class Command(BaseCommand):
    help = "Load photos into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe", action="store_true", help="Wipe all boxes before loading"
        )
        parser.add_argument(
            "--year", help="Year to assign to photographs", action="store_true"
        )
        parser.add_argument("folder", nargs="+", type=str)

    def handle(self, *args, **options):
        assigned_year = int(options["year"])
        photograph_models.Photographobjects.all().delete()
        folder_path = "0000_62_General_Photograph_Collection/Negatives/1963"
        full_path = "/vol/images/" + folder_path
        print(full_path)
        collection = collection_models.Collection.objects.get_or_create(
            label=folder_path
        )[0]

        imagefiles = glob(full_path + "/*.jp2")
        print(imagefiles)

        for image_path in imagefiles:
            base_image_path = image_path.replace("/vol/images/", "")
            print(base_image_path)
            newimage = photograph_models.Photograph.objects.create(
                image_path=base_image_path,
                date_early=datetime.date(assigned_year, 1, 1),
                date_late=datetime.date(assigned_year, 12, 31),
                digitized_date=datetime.date.today(),
                collection=collection,
            )
