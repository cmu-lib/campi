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
            "--n_trees", help="Index with this number of trees to use", type=int
        )
        parser.add_argument(
            "--max_neighbors",
            help="Maximum number of neighbors to allow into a match set",
            type=int,
        )
        parser.add_argument(
            "--cutoff_distance", help="Maximum distance to include matches", type=float
        )
        parser.add_argument(
            "--exclude_future_distance",
            help="Under this distance, pictures will not be added to repeat match groups",
            type=float,
        )

    def handle(self, *args, **options):
        pytorch_model = cv.models.PyTorchModel.objects.get(label=options["model"][0])
        annoy_idx = cv.models.AnnoyIdx.objects.get_or_create(
            pytorch_model=pytorch_model, n_trees=options["n_trees"]
        )[0]

        close_match_run = cv.models.CloseMatchRun.objects.get_or_create(
            pytorch_model=pytorch_model,
            annoy_idx=annoy_idx,
            max_neighbors=options["max_neighbors"],
            cutoff_distance=options["cutoff_distance"],
            exclude_future_distance=options["exclude_future_distance"],
        )
        if not close_match_run[1]:
            print("Resuming match")

        close_match_run[0].generate_match_sets()
