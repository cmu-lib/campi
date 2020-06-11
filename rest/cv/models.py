from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.db import transaction
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
from sklearn import cluster


class PyTorchModel(uniqueLabledModel, descriptionModel, dateModifiedModel):
    """
    All CV models must describe a set of dimensions and provide a build_embeddings method
    """

    n_dimensions = models.PositiveIntegerField()


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


class AnnoyIdx(models.Model):
    pytorch_model = models.ForeignKey(
        PyTorchModel, on_delete=models.CASCADE, related_name="pytorch_model_ann_indices"
    )
    n_trees = models.PositiveIntegerField()
    index_file = models.FilePathField(
        path=settings.DIST_INDICES_PATH, unique=True, null=True, blank=True
    )

    @property
    def index_built(self):
        return self.index_file is not None

    class Meta:
        unique_together = ("pytorch_model", "n_trees")

    @transaction.atomic
    def generate_index(self, overwrite=False):
        if self.index_file is None:
            Exception(
                "This model has not been calculated yet. Run build_embeddings_matrix() first"
            )
        if self.index_file is not None and not overwrite:
            Exception(
                f"Distance matrix '{self}' already has a built index at {self.index_file}. To overwrite, call generate_index(overwrite=True)"
            )

        print("Registering embedding ordering")
        ordered_embeddings = self.pytorch_model.embeddings.all().order_by("id")
        for i, e in enumerate(ordered_embeddings):
            IndexEmbedding.objects.create(annoy_idx=self, embedding=e, sequence=i)

        # Generate matrix
        disk_path = f"{settings.DIST_INDICES_PATH}/{self.id}.ix"
        embed_dims = self.pytorch_model.n_dimensions
        print(embed_dims)
        print(self.indexed_embeddings.count())
        ix = annoy.AnnoyIndex(f=embed_dims, metric="angular")
        ix.on_disk_build(disk_path)
        for pic in tqdm(self.indexed_embeddings.all()):
            if pic.embedding.array is not None:
                ix.add_item(pic.sequence, pic.embedding.array)
            else:
                ix.add_item(pic.sequence, [0] * embed_dims)
        print("Building index")
        ix.build(n_trees=self.n_trees)

        self.index_file = disk_path
        self.save()

    def get_nn(self, photo, n_neighbors=20):
        """
        Get n_neighbors approximate nearest neighbors
        """

        if self.index_file is None:
            Exception("Index has not yet been generated")

        # load index
        ix = annoy.AnnoyIndex(self.pytorch_model.n_dimensions, "angular")
        ix.load(self.index_file)
        pic_index = (
            self.indexed_embeddings.filter(embedding__photograph=photo).first().sequence
        )
        nn_indices, nn_distances = ix.get_nns_by_item(
            pic_index, n=n_neighbors, include_distances=True
        )

        photographs = [
            photograph.models.Photograph.objects.get(
                embeddings__indexed_embeddings__annoy_idx=self,
                embeddings__indexed_embeddings__sequence=i,
            )
            for i in nn_indices
        ]

        return {"photographs": photographs, "distances": nn_distances}


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


class IndexEmbedding(sequentialModel):
    annoy_idx = models.ForeignKey(
        AnnoyIdx, on_delete=models.CASCADE, related_name="indexed_embeddings"
    )
    embedding = models.ForeignKey(
        Embedding, on_delete=models.CASCADE, related_name="indexed_embeddings"
    )

    class Meta:
        unique_together = ("annoy_idx", "embedding", "sequence")


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
                photolist = [
                    value
                    for key, value in photograph.models.Photograph.objects.in_bulk(
                        photographs
                    ).items()
                ]
                cms_members = [
                    CloseMatchSetMembership(
                        close_match_set=cms, photograph=p, distance=0.1
                    )
                    for p in photolist
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
                        additional_photo_indices = set(new_photo_indices) - set(
                            photo_indices
                        )
                        additional_photographs = [
                            embedding_photo_ids[i] for i in additional_photo_indices
                        ]
                        additional_photolist = [
                            value
                            for key, value in photograph.models.Photograph.objects.in_bulk(
                                additional_photographs
                            ).items()
                        ]
                        new_cms_members = [
                            CloseMatchSetMembership(
                                close_match_set=cms, photograph=p, distance=0.2
                            )
                            for p in additional_photolist
                        ]
                        CloseMatchSetMembership.objects.bulk_create(new_cms_members)
        print(
            self.close_match_sets.annotate(n_images=models.Count("memberships"))
            .order_by("-n_images")
            .values_list("n_images")
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
    invalid = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Has this set been rendered redundant because its seed photograph has been matched to another set, or because its member photos have all been matched to sets?",
    )

    class Meta:
        unique_together = ("close_match_run", "representative_photograph")


class CloseMatchSetMembership(models.Model):
    close_match_set = models.ForeignKey(
        CloseMatchSet, on_delete=models.CASCADE, related_name="memberships"
    )
    photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="close_match_memberships",
    )
    distance = models.FloatField()
    accepted = models.NullBooleanField(
        default=None, help_text="Has this membership been validated by an editor?"
    )
    invalid = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Has this member photo already been matched in another set?",
    )

    class Meta:
        unique_together = ("close_match_set", "photograph")
