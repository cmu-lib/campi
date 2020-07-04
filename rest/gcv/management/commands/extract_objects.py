from django.core.management.base import BaseCommand
from gcv.models import GCVResponse
from photograph.models import ObjectAnnotation
from tqdm import tqdm


class Command(BaseCommand):
    help = "Extract ObjectAnnotations from GCVResponse data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Wipe all object annotations before re-loading from GCV response results",
        )

    def handle(self, *args, **options):
        if options["wipe"]:
            print("Deleting existing faces")
            ObjectAnnotation.objects.all().delete()
        for res in tqdm(GCVResponse.objects.all()):
            res.extract_objects()

