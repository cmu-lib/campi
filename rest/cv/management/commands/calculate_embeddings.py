from django.core.management.base import BaseCommand
import photograph
import cv


class Command(BaseCommand):
    help = "Create a set of embeddings"

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            nargs="+",
            help="Name of pytorch model whose embedding method has already been defined in cv.models",
            type=str,
        )
        parser.add_argument(
            "--label", action="store", help="label to add to this model"
        )
        parser.add_argument(
            "--n-dimensions",
            action="store",
            help="Number of dimensions in the embeddings produced by this model",
        )

    def handle(self, *args, **options):
        torch_model = getattr(cv.models, options["model"][0]).objects.get_or_create(
            label=options["label"], n_dimensions=int(options["n_dimensions"])
        )[0]
        allpics = photograph.models.Photograph.objects.all()
        torch_model.build_embeddings(allpics)
