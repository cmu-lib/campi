from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, Case, When
from campi.models import (
    uniqueLabledModel,
    descriptionModel,
    sequentialModel,
    dateModifiedModel,
    userModifiedModel,
)
import photograph
import annoy
import pickle
import torch
import requests
from PIL import Image
from torchvision import transforms
from io import BytesIO
from tqdm import tqdm
import numpy as np
from sklearn import cluster, metrics


class PyTorchModel(uniqueLabledModel, descriptionModel, dateModifiedModel):
    """
    All CV models must describe a set of dimensions and provide a build_embeddings method
    """

    n_dimensions = models.PositiveIntegerField()
    annoy_idx_file = models.FilePathField(
        path=settings.DIST_INDICES_PATH, unique=True, null=True, blank=True
    )
    photo_indices = ArrayField(models.PositiveIntegerField(), null=True)

    @property
    def index_built(self):
        return self.annoy_idx_file is not None

    def generate_index(self, embeddings_queryset, n_trees=50):
        photo_ordered_embeddings = embeddings_queryset.order_by("photograph__id")

        photo_indices = list(
            photo_ordered_embeddings.values_list("photograph__id", flat=True)
        )

        ix = annoy.AnnoyIndex(f=self.n_dimensions, metric="angular")
        for i, pic in enumerate(photo_ordered_embeddings):
            if pic.array is not None:
                ix.add_item(i, pic.array)
            else:
                ix.add_item(i, [0] * embed_dims)
        print("Building index")
        ix.build(n_trees=n_trees)

        return {"index": ix, "photo_indices": photo_indices}

    def store_index(self, n_trees=20, overwrite=False):
        if self.index_built and not overwrite:
            Exception(
                f"Model '{self.label}' already has a built index. To overwrite, call generate_index(overwrite=True)"
            )

        annoy_res = self.generate_index(
            n_trees=n_trees, embeddings_queryset=self.embeddings.all()
        )
        index_filename = f"{settings.DIST_INDICES_PATH}/{self.id}-{self.label}.ix"
        annoy_res["index"].save(fn=index_filename)
        print("storing photo indices")
        self.annoy_idx_file = index_filename
        self.photo_indices = annoy_res["photo_indices"]
        self.save()

    def get_nn(self, photo, n_neighbors=20):
        """
        Get n_neighbors approximate nearest neighbors
        """

        if self.index_built:
            Exception("Index has not yet been generated")

        # load index
        ix = annoy.AnnoyIndex(self.n_dimensions, "angular")
        ix.load(self.annoy_idx_file)
        pic_index = self.photo_indices.index(photo.id)
        nn_indices, nn_distances = ix.get_nns_by_item(
            pic_index, n=n_neighbors, include_distances=True
        )

        distance_cases = [
            When(id=self.photo_indices[nn_indices[i]], then=d)
            for i, d in enumerate(nn_distances)
        ]

        # Annotate a queryset of photos with the distances, so we can return a queryset instead of a dict. More efficient to add on necessary select_related/prefetch_related before passing to a serializer

        nn_photos = (
            photograph.models.Photograph.objects.filter(
                id__in=[self.photo_indices[i] for i in nn_indices]
            )
            .annotate(
                distance=Case(
                    *distance_cases, default=0, output_field=models.FloatField()
                )
            )
            .order_by("distance")
        )

        return nn_photos

    def get_arbitrary_nn(self, photo, photo_queryset, n_neighbors=20):
        embeddings_queryset = photo_queryset.embeddings.filter(
            pytorch_model=self, photograph__in=photo_queryset
        )

        # Generate a custom index based on the specified queryset
        temp_idx = self.generate_index(embeddings_queryset)

        photo_indices = list(
            embeddings_queryset.values_list("photograph__id", flat=True)
        )

        search_vector = self.embeddings.filter(photograph=photo)[0].array

        nn_indices, nn_distances = temp_idx.get_nns_by_vector(
            search_vector, n=n_neighbors, include_distances=True
        )

        distance_cases = [
            When(id=photo_indices[nn_indices[i]], then=d)
            for i, d in enumerate(nn_distances)
        ]

        # Annotate a queryset of photos with the distances, so we can return a queryset instead of a dict. More efficient to add on necessary select_related/prefetch_related before passing to a serializer

        nn_photos = (
            photograph.models.Photograph.objects.filter(
                id__in=[self.photo_indices[i] for i in nn_indices]
            )
            .annotate(
                distance=Case(
                    *distance_cases, default=0, output_field=models.FloatField()
                )
            )
            .order_by("distance")
        )

        return nn_photos


class ColorInceptionV3(PyTorchModel):
    class Meta:
        proxy = True

    def build_embeddings(self, photograph_queryset):
        """
        Take a queryset of photographs and calculate their embeddings

        https://towardsdatascience.com/finding-similar-images-using-deep-learning-and-locality-sensitive-hashing-9528afee02f5

        https://pytorch.org/hub/pytorch_vision_inception_v3/
        """

        print("Loading inception v3 model")
        model = torch.hub.load("pytorch/vision:v0.5.0", "resnet18", pretrained=True)
        print("Model downloaded. Begin eval")
        model.eval()
        print("Eval finished")
        embeddings_model = torch.nn.Sequential(*list(model.children())[:-1])

        preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        already_calculated_embeddings = self.embeddings.all()
        # From the supplied photographs, find the ones that haven't had embeddings created yet for the current model
        embeddings_to_be_calculated = photograph_queryset.exclude(
            embeddings__in=already_calculated_embeddings
        ).all()

        for pic in tqdm(embeddings_to_be_calculated):
            try:
                squared_small_path = f"{pic.iiif_base}/full/299,299/0/default.jpg"

                res = requests.get(squared_small_path)
                img = Image.open(BytesIO(res.content))

                # If image is grayscale, convert it to a false RGB
                if img.mode == "L":
                    img_array = np.repeat(np.array(img)[..., np.newaxis], 3, -1)
                    # Convert to a false rgb image
                    rgb_img = Image.fromarray(img_array)
                else:
                    rgb_img = img

                input_tensor = preprocess(rgb_img)
                input_batch = input_tensor.unsqueeze(0)

                with torch.no_grad():
                    output = np.array(embeddings_model(input_batch).flatten())
                    embedding_list = output.tolist()
                    Embedding.objects.create(
                        pytorch_model=self, photograph=pic, array=embedding_list
                    )
            except:
                print(f"Error processing {pic.full_image}")
                continue


class GrayInceptionV3(PyTorchModel):
    class Meta:
        proxy = True

    def build_embeddings(self, photograph_queryset):
        """
        Take a queryset of photographs and calculate their embeddings

        https://towardsdatascience.com/finding-similar-images-using-deep-learning-and-locality-sensitive-hashing-9528afee02f5

        https://pytorch.org/hub/pytorch_vision_inception_v3/
        """

        print("Loading inception v3 model")
        model = torch.hub.load("pytorch/vision:v0.5.0", "resnet18", pretrained=True)
        print("Model downloaded. Begin eval")
        model.eval()
        print("Eval finished")
        embeddings_model = torch.nn.Sequential(*list(model.children())[:-1])

        preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        already_calculated_embeddings = self.embeddings.all()
        # From the supplied photographs, find the ones that haven't had embeddings created yet for the current model
        embeddings_to_be_calculated = photograph_queryset.exclude(
            embeddings__in=already_calculated_embeddings
        ).all()

        for pic in tqdm(embeddings_to_be_calculated):
            try:
                squared_small_path = f"{pic.iiif_base}/full/299,299/0/gray.jpg"

                res = requests.get(squared_small_path)
                img = Image.open(BytesIO(res.content))

                # If image is grayscale, convert it to a false RGB
                if img.mode == "L":
                    img_array = np.repeat(np.array(img)[..., np.newaxis], 3, -1)
                    # Convert to a false rgb image
                    rgb_img = Image.fromarray(img_array)
                else:
                    rgb_img = img

                input_tensor = preprocess(rgb_img)
                input_batch = input_tensor.unsqueeze(0)

                with torch.no_grad():
                    output = np.array(embeddings_model(input_batch).flatten())
                    embedding_list = output.tolist()
                    Embedding.objects.create(
                        pytorch_model=self, photograph=pic, array=embedding_list
                    )
            except:
                print(f"Error processing {pic.full_image}")
                continue


class BitonalInceptionV3(PyTorchModel):
    class Meta:
        proxy = True

    def build_embeddings(self, photograph_queryset):
        """
        Take a queryset of photographs and calculate their embeddings

        https://towardsdatascience.com/finding-similar-images-using-deep-learning-and-locality-sensitive-hashing-9528afee02f5

        https://pytorch.org/hub/pytorch_vision_inception_v3/
        """

        print("Loading inception v3 model")
        model = torch.hub.load("pytorch/vision:v0.5.0", "resnet18", pretrained=True)
        print("Model downloaded. Begin eval")
        model.eval()
        print("Eval finished")
        embeddings_model = torch.nn.Sequential(*list(model.children())[:-1])

        preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        already_calculated_embeddings = self.embeddings.all()
        # From the supplied photographs, find the ones that haven't had embeddings created yet for the current model
        embeddings_to_be_calculated = photograph_queryset.exclude(
            embeddings__in=already_calculated_embeddings
        ).all()

        for pic in tqdm(embeddings_to_be_calculated):
            try:
                squared_small_path = f"{pic.iiif_base}/full/299,299/0/bitonal.jpg"

                res = requests.get(squared_small_path)
                img = Image.open(BytesIO(res.content))

                # If image is grayscale, convert it to a false RGB
                if img.mode == "L":
                    img_array = np.repeat(np.array(img)[..., np.newaxis], 3, -1)
                    # Convert to a false rgb image
                    rgb_img = Image.fromarray(img_array)
                else:
                    rgb_img = img

                input_tensor = preprocess(rgb_img)
                input_batch = input_tensor.unsqueeze(0)

                with torch.no_grad():
                    output = np.array(embeddings_model(input_batch).flatten())
                    embedding_list = output.tolist()
                    Embedding.objects.create(
                        pytorch_model=self, photograph=pic, array=embedding_list
                    )
            except:
                print(f"Error processing {pic.full_image}")
                continue


class Embedding(models.Model):
    pytorch_model = models.ForeignKey(
        PyTorchModel, on_delete=models.CASCADE, related_name="embeddings"
    )
    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="embeddings",
    )
    array = ArrayField(models.FloatField())

    class Meta:
        unique_together = ("pytorch_model", "photograph")
        ordering = ["pytorch_model"]


class CloseMatchRun(dateModifiedModel):
    pytorch_model = models.ForeignKey(
        PyTorchModel, on_delete=models.CASCADE, related_name="close_match_runs"
    )
    cutoff_distance = models.FloatField(
        help_text="Photographs returned from the index query farther away from the photograph will be excluded."
    )
    min_samples = models.PositiveIntegerField(default=2, help_text="")
    exclude_future_distance = models.FloatField(
        help_text="Photographs returned from the index query farther away than this measure will be excluded from future consideration from any CloseMatchSet in this run."
    )

    class Meta:
        unique_together = (
            "pytorch_model",
            "cutoff_distance",
            "exclude_future_distance",
            "min_samples",
        )

    def generate_clusters_dbscan(self):
        """
        Use sklearn's dbscan to generate clusters
        """
        print("Collecting embeddings")
        ordered_embeddings = self.pytorch_model.embeddings.order_by("id")
        embedding_photo_ids = list(
            ordered_embeddings.values_list("photograph__id", flat=True)
        )
        embedding_matrix = np.array(ordered_embeddings.values_list("array", flat=True))

        print("Minimum clusters")
        min_clusters = cluster.dbscan(
            embedding_matrix,
            metric="cosine",
            min_samples=self.min_samples,
            eps=self.exclude_future_distance,
        )
        print("Maximum clusters")
        max_clusters = cluster.dbscan(
            embedding_matrix,
            metric="cosine",
            min_samples=self.min_samples,
            eps=self.cutoff_distance,
        )
        # Regroup indices by membership before creating sets
        min_memberships = {str(i): [] for i in set(min_clusters[1]) if i != -1}
        print("Mapping membership ids")
        for i, membership in enumerate(min_clusters[1]):
            if membership != -1:
                min_memberships[str(membership)].append(i)
        for membership_id in tqdm(set(min_clusters[1])):
            if membership_id != -1:
                cms = CloseMatchSet.objects.create(close_match_run=self)
                photo_indices = min_memberships[str(membership_id)]
                photographs = [embedding_photo_ids[i] for i in photo_indices]
                photolist = photograph.models.Photograph.objects.in_bulk(photographs)
                cosine_distances = list(
                    metrics.pairwise.cosine_distances(
                        X=embedding_matrix[[photo_indices[0]],],
                        Y=embedding_matrix[photo_indices,],
                    )[0,]
                )
                cms_members = [
                    CloseMatchSetMembership(
                        close_match_set=cms,
                        photograph=photolist[p],
                        core=True,
                        distance=cosine_distances[i],
                    )
                    for i, p in enumerate(photographs)
                ]
                CloseMatchSetMembership.objects.bulk_create(cms_members)
                # Find the sets that these pics belong to in the wider clusters, and add those photos to this set as well
                larger_groups = set(
                    [
                        x
                        for i, x in enumerate(list(max_clusters[1]))
                        if i in photo_indices
                    ]
                )
                for group in larger_groups:
                    if group != -1:
                        new_photo_indices = [
                            i for i, x in enumerate(max_clusters[1]) if x == group
                        ]
                        # Find those photos that haven't already been added to this set
                        additional_photo_indices = list(
                            set(new_photo_indices) - set(photo_indices)
                        )
                        if len(additional_photo_indices) > 0:
                            additional_photographs = [
                                embedding_photo_ids[i] for i in additional_photo_indices
                            ]
                            additional_photolist = photograph.models.Photograph.objects.in_bulk(
                                additional_photographs
                            )
                            new_cosine_distances = list(
                                metrics.pairwise.cosine_distances(
                                    X=embedding_matrix[[photo_indices[0]],],
                                    Y=embedding_matrix[additional_photo_indices,],
                                )[0,]
                            )
                            new_cms_members = [
                                CloseMatchSetMembership(
                                    close_match_set=cms,
                                    photograph=additional_photolist[p],
                                    core=False,
                                    distance=new_cosine_distances[i],
                                )
                                for i, p in enumerate(additional_photographs)
                            ]
                            CloseMatchSetMembership.objects.bulk_create(new_cms_members)
        print(
            self.close_match_sets.annotate(n_images=models.Count("memberships"))
            .order_by("-n_images")
            .values_list("n_images")
        )

    def tidy_clusters(self):
        """
        Check for duplicated filenames in sets of 2, and automatically mark those as done.
        """
        duo_sets = (
            self.close_match_sets.annotate(
                n_images=Count(
                    "memberships", filter=Q(memberships__core=True), unique=True
                )
            )
            .filter(n_images=2, user_last_modified__isnull=True)
            .all()
        )

        for cms in tqdm(duo_sets):
            setnames = {
                m.photograph.filename for m in cms.memberships.filter(core=True).all()
            }
            if len(setnames) == 1:
                print(setnames)
                cms.memberships.filter(core=True).update(
                    state=CloseMatchSetMembership.ACCEPTED
                )
                cms.representative_photograph = (
                    cms.memberships.filter(core=True).first().photograph
                )
                cms.user_last_modified = User.objects.first()
                cms.save()

                accepted_photographs = photograph.models.Photograph.objects.filter(
                    close_match_memberships__close_match_set=cms,
                    close_match_memberships__state=CloseMatchSetMembership.ACCEPTED,
                ).distinct()

                CloseMatchSetMembership.objects.filter(
                    close_match_set__close_match_run=self,
                    close_match_set__user_last_modified__isnull=True,
                    photograph__in=accepted_photographs,
                ).exclude(state=CloseMatchSetMembership.ACCEPTED).all().update(
                    state=CloseMatchSetMembership.OTHER_SET
                )


class CloseMatchRunConsidered(models.Model):
    close_match_run = models.ForeignKey(
        CloseMatchRun,
        on_delete=models.CASCADE,
        related_name="considered_photo_membership",
    )
    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="considered_photo_membership",
    )

    class Meta:
        unique_together = ("close_match_run", "photograph")


class CloseMatchSet(dateModifiedModel, userModifiedModel):
    close_match_run = models.ForeignKey(
        CloseMatchRun, on_delete=models.CASCADE, related_name="close_match_sets"
    )
    photographs = models.ManyToManyField(
        photograph.models.Photograph,
        through="CloseMatchSetMembership",
        through_fields=("close_match_set", "photograph"),
    )
    representative_photograph = models.ForeignKey(
        photograph.models.Photograph,
        null=True,
        on_delete=models.CASCADE,
        related_name="representative_of_sets",
    )
    has_duplicates = models.BooleanField(
        default=False,
        help_text="Does this set contain exact duplicates / copy-negatives?",
    )

    class Meta:
        unique_together = ("close_match_run", "representative_photograph")


class CloseMatchSetMembership(models.Model):
    NOT_REVIEWED = "n"
    ACCEPTED = "a"
    REJECTED = "r"
    OTHER_SET = "o"
    EXCLUDED = "e"
    MEMBERSHIP_STATE_CHOICES = [
        (NOT_REVIEWED, "Not yet reviewed"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (OTHER_SET, "Already matched in other set"),
        (EXCLUDED, "Explicitly excluded from any consideration by an editor"),
    ]

    close_match_set = models.ForeignKey(
        CloseMatchSet, on_delete=models.CASCADE, related_name="memberships"
    )
    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="close_match_memberships",
    )
    distance = models.FloatField(
        null=True,
        db_index=True,
        help_text="Cosine distance from the first membership added to this set",
    )
    core = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Is this membership part of the core cluster or added in the second pass?",
    )
    state = models.CharField(
        max_length=1,
        blank=False,
        null=False,
        default=NOT_REVIEWED,
        choices=MEMBERSHIP_STATE_CHOICES,
        db_index=True,
        help_text="Status of this membership (e.g. accepted, rejected)",
    )
    user_added = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Was this match manually added by a user?",
    )

    class Meta:
        unique_together = ("close_match_set", "photograph")
