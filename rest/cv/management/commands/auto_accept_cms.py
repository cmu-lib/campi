from django.core.management.base import BaseCommand
from django.db.models import Count, Q, F, ExpressionWrapper, BooleanField
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
import cv


class Command(BaseCommand):
    help = "Auto-accept the remainder of the close match sets in a specified close match run"

    def add_arguments(self, parser):
        parser.add_argument(
            "cmr",
            nargs="+",
            help="ID of the Close Match Run to be auto-accepted",
            type=int,
        )

    def handle(self, *args, **options):
        close_match_run = cv.models.CloseMatchRun.objects.get(id=options["cmr"][0])
        unreviewed_sets = (
            close_match_run.close_match_sets.annotate(
                n_images=Count("memberships"),
                n_redundant_images=Count(
                    "memberships",
                    filter=Q(
                        memberships__state=cv.models.CloseMatchSetMembership.OTHER_SET
                    )
                    | Q(memberships__state=cv.models.CloseMatchSetMembership.EXCLUDED),
                ),
                n_valid_images=F("n_images") - F("n_redundant_images"),
                redundant=ExpressionWrapper(
                    Q(n_valid_images__lte=1), output_field=BooleanField()
                ),
            )
            .filter(user_last_modified__isnull=True, redundant=False)
            .order_by("-n_images")
        )
        while unreviewed_sets.exists():
            next_set = unreviewed_sets.first()
            print(next_set.id)
            res = next_set.approve(
                accepted_memberships=next_set.memberships.all(),
                rejected_memberships=[],
                excluded_memberships=[],
                representative_photograph=next_set.memberships.first().photograph,
                has_duplicates=False,
                user=User.objects.get(username="mlincoln"),
            )
