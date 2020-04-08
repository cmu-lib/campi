from django.core.management.base import BaseCommand
from photograph import models as photograph_models
from cv import models as cv_models


class Command(BaseCommand):
    help = "Create a set of embeddings"

    # def add_arguments(self, parser):
    #     # parser.add_argument(
    #     #     "--wipe", action="store_true", help="Wipe all images before loading"
    #     # )
    #     # parser.add_argument("manifest", nargs="+", type=str)

    def handle(self, *args, **options):
        # cv_models.Embeddings.objects.all().delete()
        # # Get 100 photographs
        # pics100 = photograph_models.Photograph.objects.all()[:100]
        # allpics = photograph_models.Photograph.objects.all()
        # inet = cv_models.Embeddings.create(
        #     photograph_queryset=pics100,
        #     label="100-resnet",
        #     description="100 photos using resnetpython ",
        # )
        # anet = cv_models.Embeddings.create(
        #     photograph_queryset=allpics,
        #     label="all-resnet",
        #     description="All photos using resnetpython ",
        # )
        # cv_models.Embeddings.objects.get(label="100-resnet").build_embeddings_matrix()
        for e in cv_models.Embeddings.objects.all():
            if not e.are_embeddings_calculated:
                print(e)
                e.build_embeddings_matrix()
