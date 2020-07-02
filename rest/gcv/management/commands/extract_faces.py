from django.core.management.base import BaseCommand
from gcv.models import GCVResponse
from tqdm import tqdm


class Command(BaseCommand):
    help = "Extract FaceAnnotations from GCVResponse data"

    def handle(self, *args, **options):
        for res in GCVResponse.objects.all():
            res.extract_faces()

