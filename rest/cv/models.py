from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.db import transaction
from campi.models import (
    uniqueLabledModel,
    descriptionModel,
    sequentialModel,
    dateModifiedModel,
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


class PyTorchModel(uniqueLabledModel, descriptionModel, dateModifiedModel):
    n_dimensions = models.PositiveIntegerField()

    # @classmethod
    # def from_db(cls, db, firled_names, values):
    # possibly override from_db to load the index file into memory when the instance is loaded from the database. Not sure if this would work with caching or repeated calls to an API

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

    # @classmethod
    # @transaction.atomic
    # def create(cls, photograph_queryset, *args, **kwargs):
    #     """
    #     An index is only relevant for a specified corpus, so when creating an index you must specify the set of photogs to be covered by it
    #     """
    #     dm = cls(*args, **kwargs)
    #     dm.save()
    #     ordered_photoset = photograph_queryset.order_by("id")
    #     for i, pic in enumerate(ordered_photoset):
    #         IndexEmbedding.objects.create(annoy_idx=self, photograph=pic, sequence=i)
    #     return dm

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
        print(ix.get_n_items())
        print(ix.get_n_trees())
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
    annoy_idx = models.ForeignKey(
        AnnoyIdx, on_delete=models.CASCADE, related_name="close_match_runs"
    )
    max_neighbors = models.PositiveIntegerField(
        help_text="Number of nearest neighbors to request from the index.", default=6
    )
    cutoff_distance = models.FloatField(
        help_text="Photographs returned from the index query farther away from the photograph will be excluded."
    )
    exclude_future_distance = models.FloatField(
        help_text="Photographs returned from the index query farther away than this measure will be excluded from future consideration from any CloseMatchSet in this run."
    )

    class Meta:
        unique_together = (
            "pytorch_model",
            "annoy_idx",
            "max_neighbors",
            "cutoff_distance",
            "exclude_future_distance",
        )


class CloseMatchSet(dateModifiedModel):
    close_match_run = models.ForeignKey(
        CloseMatchRun, on_delete=models.CASCADE, related_name="close_match_sets"
    )
    seed_photograph = models.ForeignKey(
        photograph.models.Photograph,
        on_delete=models.CASCADE,
        related_name="seeded_close_match_sets",
    )

    class Meta:
        unique_together = ("close_match_run", "seed_photograph")


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

    class Meta:
        unique_together = ("close_match_set", "photograph")
