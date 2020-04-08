from django.core.management.base import BaseCommand
from photograph import models as photograph_models
from cv import models as cv_models


class Command(BaseCommand):
    help = "Calculate annoy indices"

    def handle(self, *args, **options):
        embed = cv_models.Embeddings.objects.get(label="all-resnet")
        embed.generate_index(overwrite=True)
