from django.core.management.base import BaseCommand
import photograph
import cv


class Command(BaseCommand):
    help = "Calculate annoy indices for the embeddings produced by a pytorch model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            action="store_true",
            help="Name of pytorch model whose embeddings have already been run",
            type=str,
        )
        parser.add_argument(
            "--n_trees",
            action="store_true",
            help="Nubmer of trees to grow for the model (50 is a good start)",
            type=int,
        )

    def handle(self, *args, **options):
        pytorch_model = cv.models.PyTorchModel.objects.get(label=args["model"])
        annoy_idx = AnnoyIdx(pytorch_model=pytorch_model, n_trees=args["n_trees"])
        annoy_idx.save()
        annoy_idx.generate_index()
