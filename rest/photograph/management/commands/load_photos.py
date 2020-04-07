from django.core.management.base import BaseCommand
from photograph import models as photograph_models
from collection import models as collection_models
from tqdm import tqdm
from glob import glob
import datetime
import json
import re


class Command(BaseCommand):
    help = "Load photos into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe", action="store_true", help="Wipe all images before loading"
        )
        parser.add_argument("manifest", nargs="+", type=str)

    def handle(self, *args, **options):
        photograph_models.Photograph.objects.all().delete()
        collection_models.Collection.objects.all().delete()
        manifest = json.load(open(options["manifest"][0], "rb"))
        for item in tqdm(manifest):
            split_path = item.split("/")
            for i, coll in enumerate(split_path[:-1]):
                collection_res = collection_models.Collection.objects.get_or_create(
                    label=coll
                )
                collection = collection_res[0]
                if collection_res[1] == True and i != 0:
                    # If a new collection, make sure to assign its parent
                    collection.parent_collection = collection_models.Collection.objects.get(
                        label=split_path[i - 1]
                    )
                    collection.save()

            newimage = photograph_models.Photograph.objects.create(
                image_path=item,
                date_early=datetime.date(1900, 1, 1),
                date_late=datetime.date(2000, 12, 31),
                digitized_date=datetime.date.today(),
                collection=collection_models.Collection.objects.get(
                    label=split_path[-2]
                ),
            )
