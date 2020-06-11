from django.core.management.base import BaseCommand
from django.db import transaction
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
        parser.add_argument("--min_samples", help="Minimum samples", type=int)
        parser.add_argument(
            "--cutoff_distance", help="Maximum distance to include matches", type=float
        )
        parser.add_argument(
            "--exclude_future_distance",
            help="Under this distance, pictures will not be added to repeat match groups",
            type=float,
        )

    @transaction.atomic
    def handle(self, *args, **options):
        pytorch_model = cv.models.PyTorchModel.objects.get(label=options["model"][0])
        close_match_run = cv.models.CloseMatchRun.objects.get_or_create(
            pytorch_model=pytorch_model,
            min_samples=options["min_samples"],
            cutoff_distance=options["cutoff_distance"],
            exclude_future_distance=options["exclude_future_distance"],
        )

        close_match_run[0].generate_clusters_dbscan()
