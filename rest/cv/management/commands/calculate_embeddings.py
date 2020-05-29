from django.core.management.base import BaseCommand
import photograph
import cv


class Command(BaseCommand):
    help = "Create a set of embeddings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            action="store_true",
            help="Name of pytorch model whose embedding method has already been defined in cv.models",
            type=str,
        )
        parser.add_argument(
            "--label", action="store_true", help="label to add to this model", type=str
        )
        parser.add_argument(
            "--n_dimensions",
            action="store_true",
            help="Number of dimensions in the embeddings produced by this model",
            type=int,
        )

    def handle(self, *args, **options):
        torch_model = getattr(cv.models, args["model"]).objects.get_or_create(
            label=args["label"], n_dimensions=args["n_dimensions"]
        )[0]
        allpics = photograph.models.Photograph.objects.all()
        torch_model.build_embeddings(allpics)
