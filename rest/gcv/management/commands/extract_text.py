from django.core.management.base import BaseCommand
from gcv.models import GCVResponse
from photograph.models import TextAnnotation, Photograph
from tqdm import tqdm


class Command(BaseCommand):
    help = "Extract TextAnnotations from GCVResponse data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Wipe all text annotations before re-loading from GCV response results",
        )

    def handle(self, *args, **options):
        if options["wipe"]:
            print("Deleting existing text")
            TextAnnotation.objects.all().delete()
            Photograph.objects.all().update(image_text="")
        for res in tqdm(GCVResponse.objects.all()):
            res.extract_text()

