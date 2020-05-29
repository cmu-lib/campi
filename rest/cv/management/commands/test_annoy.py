from django.core.management.base import BaseCommand
import photograph
import cv


class Command(BaseCommand):
    help = "Test annoy indices"

    def handle(self, *args, **options):
        buggypic = photograph.models.Photograph.objects.order_by(
            "-digitized_date"
        ).first()
        e1 = cv.models.AnnoyIdx.objects.first()
        print("starting to collect")
        photoset = e1.get_nn(buggypic)
        print("collected")
        print(photoset)
