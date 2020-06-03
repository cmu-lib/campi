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
            "--n-trees", help="Index with this number of trees to use", type=int
        )
        parser.add_argument(
            "--max-neighbors",
            help="Maximum number of neighbors to allow into a match set",
            type=int,
        )
        parser.add_argument(
            "--cutoff-distance", help="Maximum distance to include matches", type=float
        )
        parser.add_argument(
            "--auto-distance",
            help="Under this distance, pictures will not be added to repeat match groups",
            type=float,
        )

    def create_set(close_match_run, photograph):
        photo_neighbors = close_match_run.annoy_idx.get_nn(
            photograph, n_neighbors=close_match_run.cutoff_distance
        )

    def handle(self, *args, **options):
        pytorch_model = cv.models.PyTorchModel.objects.get(label=options["model"][0])
        annoy_idx = cv.models.AnnoyIdx.objects.get_or_create(
            pytorch_model=pytorch_model, n_trees=options["n-trees"]
        )[0]
        if not annoy_idx.index_built:
            annoy_idx.generate_index()
        close_match_run = models.CloseMatchRun.objects.get_or_create(
            pytorch_model=pytorch_model,
            annoy_idx=annoy_idx,
            max_neighbors=options["max-neighbors"],
            cutoff_distance=options["cutoff-distance"],
            auto_distance=options["auto-distance"],
        )
        # For photos not yet under the auto_distance of a close_match_run:
        already_completed_sets = close_match_run.close_match_sets.all()
        photos_to_do = pytorch_model.embeddings.exclude(
            photograph__close_match_set_memberships__in=already_completed_sets
        ).distinct()
        for photo in photos_to_do:
            photo_cmsm = models.CloseMatchSetMembership.objects.filter(
                close_match_set__close_match_run=close_match_run
            ).first()
            if photo_cmsm is None:
                create_set(close_match_run, photo)
            elif photo_cmsm.distance >= close_match_run.auto_distance:
                create_set(close_match_run, photo)
