from django.core.management.base import BaseCommand
from photograph import models as photograph_models
from cv import models as cv_models
import annoy
import pickle
import torch
import requests
import tempfile
from PIL import Image
from torchvision import transforms
from io import BytesIO


class Command(BaseCommand):
    help = "Create a set of embeddings"

    # def add_arguments(self, parser):
    #     # parser.add_argument(
    #     #     "--wipe", action="store_true", help="Wipe all images before loading"
    #     # )
    #     # parser.add_argument("manifest", nargs="+", type=str)

    def handle(self, *args, **options):
        cv_models.Embeddings.objects.all().delete()
        # Get 100 photographs
        pics100 = photograph_models.Photograph.objects.all()[:100]
        inet = cv_models.Embeddings.create(photograph_queryset=pics100)
        inet.build_embeddings_matrix()
