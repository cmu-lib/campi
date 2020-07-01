from django.core.management.base import BaseCommand
from photograph.models import Photograph
from tqdm import tqdm
import requests


class Command(BaseCommand):
    help = "Retrieve and save photo dimensions from IIIF server"

    def handle(self, *args, **options):
        for p in tqdm(Photograph.objects.filter(height=0).all()):
            try:
                p_info = requests.get(p.iiif_info).json()
                p.height = p_info["height"]
                p.width = p_info["width"]
                p.save()
            except:
                continue

