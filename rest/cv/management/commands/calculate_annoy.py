from django.core.management.base import BaseCommand
import photograph
import cv


class Command(BaseCommand):
    help = "Calculate annoy indices for the embeddings produced by a pytorch model"

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            nargs="+",
            help="Name of pytorch model whose embeddings have already been run",
        )
        parser.add_argument(
            "--n_trees",
            help="Nubmer of trees to grow for the model (50 is a good start)",
            type=int,
        )

    def handle(self, *args, **options):
        pytorch_model = cv.models.PyTorchModel.objects.get(label=options["model"][0])
        annoy_idx = cv.models.AnnoyIdx.objects.get_or_create(
            pytorch_model=pytorch_model, n_trees=options["n_trees"]
        )[0]
        annoy_idx.generate_index()
