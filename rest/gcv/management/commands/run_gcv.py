from django.core.management.base import BaseCommand
from django.conf import settings
from photograph.models import Photograph
from gcv.models import GCVResponse
from google.cloud import vision
from tqdm import tqdm
from time import sleep


class Command(BaseCommand):
    help = "Run photographs through the Google Cloud Vision API"

    def handle(self, *args, **options):
        client = vision.ImageAnnotatorClient()

        photos_for_annotation = Photograph.objects.filter(
            gcv_response__isnull=True
        ).order_by("id")
        response = None
        for p in tqdm(photos_for_annotation):
            source_url = f"{p.image['id']}/full/!{settings.GOOGLE_SIZE},{settings.GOOGLE_SIZE}/0/default.jpg"
            try:
                response = client.annotate_image(
                    {
                        "image": {"source": {"image_uri": source_url}},
                        "features": [
                            {"type": vision.enums.Feature.Type.FACE_DETECTION},
                            {"type": vision.enums.Feature.Type.LABEL_DETECTION},
                            {"type": vision.enums.Feature.Type.IMAGE_PROPERTIES},
                            {"type": vision.enums.Feature.Type.CROP_HINTS},
                            {"type": vision.enums.Feature.Type.TEXT_DETECTION},
                            {"type": vision.enums.Feature.Type.SAFE_SEARCH_DETECTION},
                            {"type": vision.enums.Feature.Type.WEB_DETECTION},
                        ],
                    }
                )
                gcv = GCVResponse(photograph=p, annotations=response)
                gcv.save()
            except:
                continue
            sleep(1)
