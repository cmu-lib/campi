from django.core.management.base import BaseCommand
from photograph import models as photograph_models
from cv import models as cv_models


class Command(BaseCommand):
    help = "Test annoy indices"

    def handle(self, *args, **options):
        e1 = cv_models.Embeddings.objects.first()
        photoset = e1.get_nn(e1.photographs.first)
        for pic in photoset:
            print(pic.full_image)
