from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from campi.models import uniqueLabledModel, descriptionModel
from photograph import models as photograph_models
import annoy
import pickle
import torch
import requests
from PIL import Image
from torchvision import transforms
from io import BytesIO
from tqdm import tqdm
import numpy as np


class Embeddings(uniqueLabledModel, descriptionModel):
    index_file = models.FilePathField(path=settings.DIST_INDICES_PATH, null=True)
    photographs = models.ManyToManyField(
        photograph_models.Photograph,
        related_name="cv_models",
        through="PhotographEmbeddings",
        through_fields=("embeddings", "photograph"),
    )

    @classmethod
    def create(cls, photograph_queryset, *args, **kwargs):
        dm = cls(*args, **kwargs)
        dm.save()
        for i, pic in enumerate(photograph_queryset):
            PhotographEmbeddings.objects.create(
                embeddings=dm, photograph=pic, sequence=i
            )
        return dm

    @property
    def are_embeddings_calculated(self):
        """
        Have embeddings for every photograph in this model been calculated yet?
        """
        return not self.photograph_embeddings.exclude(array__isnull=False).exists()

    # @classmethod
    # def from_db(cls, db, firled_names, values):
    # possibly override from_db to load the index file into memory when the instance is loaded from the database. Not sure if this would work with caching or repeated calls to an API

    def generate_index(self, overwrite=False, trees=10):
        # if self.index_file is None:
        #     Exception(
        #         "This model has not been calculated yet. Run build_embeddings_matrix() first"
        #     )
        # if self.index_file is not None and not overwrite:
        #     Exception(
        #         f"Distance matrix '{self}' already has a built index at {self.index_file}. To overwrite, call generate_index(overwrite=True)"
        #     )

        # Generate matrix
        disk_path = f"{settings.DIST_INDICES_PATH}/{self.id}.ix"
        embed_dims = len(self.photograph_embeddings.first().array)
        print(embed_dims)
        print(self.photograph_embeddings.count())
        ix = annoy.AnnoyIndex(f=embed_dims, metric="angular")
        ix.on_disk_build(disk_path)
        for pic in tqdm(self.photograph_embeddings.all()):
            if pic.array is not None:
                ix.add_item(pic.sequence, pic.array)
            else:
                ix.add_item(pic.sequence, [0] * embed_dims)
        print("Building index")
        ix.build(trees)

        self.index_file = disk_path
        self.save()

    def get_nn(self, photograph, n_neighbors=8):
        """
        Get n_neighbors approximate nearest neighbors
        """

        if self.index_file is None:
            Exception("Index has not yet been generated")

        # load index
        ix = annoy.AnnoyIndex(512, "angular")
        ix.load(self.index_file)
        print(ix.get_n_items())
        print(ix.get_n_trees())
        nn_indices = ix.get_nns_by_item(1, n=n_neighbors)
        print(nn_indices)
        # get returns
        return photograph_models.Photograph.objects.filter(id__in=nn_indices).all()

    def build_embeddings_matrix(self):
        """
        Take a queryset of photographs and build a distance matrix

        https://towardsdatascience.com/finding-similar-images-using-deep-learning-and-locality-sensitive-hashing-9528afee02f5

        https://pytorch.org/hub/pytorch_vision_inception_v3/
        """

        n_photos = self.photographs.count()

        if n_photos == 0:
            Exception("Associate photographs with the current model first")

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

        for pic in tqdm(self.photograph_embeddings.filter(array__isnull=True).all()):
            try:
                squared_small_path = (
                    f"{pic.photograph.iiif_base}/full/299,299/0/default.jpg"
                )

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
                    pic.array = output.tolist()
                    pic.save()
            except:
                print(f"Error processing {pic.photograph.full_image}")
                continue


class PhotographEmbeddings(models.Model):
    embeddings = models.ForeignKey(
        Embeddings, on_delete=models.CASCADE, related_name="photograph_embeddings"
    )
    photograph = models.ForeignKey(
        photograph_models.Photograph,
        on_delete=models.CASCADE,
        related_name="photograph_embeddings",
    )
    sequence = models.PositiveIntegerField(db_index=True)
    array = ArrayField(models.FloatField(), null=True)

    class Meta:
        unique_together = (("embeddings", "sequence"), ("embeddings", "photograph"))
        ordering = ["embeddings", "sequence"]
