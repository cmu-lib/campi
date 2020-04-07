from django.db import models
from django.conf import settings
from argus.models import labeledModel, descriptionModel, sequentialModel
from photograph import models as photograph_models
import annoy
import pickle
import torch
import requests
import tempfile
from PIL import Image
from torchvision import transforms
from io import BytesIO
import tqdm


class DistanceMatrix(descriptionModel):
    pickled_file = models.FilePathField(path=settings.DIST_MATRICES_PATH, null=True)
    index_file = models.FilePathField(path=settings.DIST_INDICES_PATH, null=True)
    photographs = models.ManyToManyField(
        photograph_models.Photograph, related_name="cv_models"
    )

    @classmethod
    def create(cls, photograph_queryset, *args, **kwargs):
        dm = cls(*args, **kwargs)
        dm.save()
        dm.photographs.set(photograph_queryset)
        return dm

    # @classmethod
    # def from_db(cls, db, firled_names, values):
    # possibly override from_db to load the index file into memory when the instance is loaded from the database. Not sure if this would work with caching or repeated calls to an API

    def generate_index(self, overwrite=False):
        if self.index_file is None:
            Exception(
                "This model has not been calculated yet. Run build_distance_matrix() first"
            )
        if self.index_file is not None and not overwrite:
            Exception(
                f"Distance matrix {self.pickled_file} already has a built index at {self.index_file}. To overwrite, call generate_index(overwrite=True)"
            )

        # Load distance matrix
        mat = pickle.load(self.pickled_file)

        # Generate matrix
        disk_path = settings.DIST_INDICES_PATH + self.id + ".pl"
        ix = annoy.AnnoyIndex(f=ncol(mat), metric="angular")
        a.on_disk_build(disk_path)
        for row, i in mat.rows().enumerate():
            ix.add_item(i, row)

        self.index_file = disk_path
        self.save()

    def get_nn(self, photograph, n_neighbors=8):
        """
        Get n_neighbors approximate nearest neighbors
        """

        if self.index_file is None:
            Exception("Index has not yet been generated")

        # load index
        ix = annoy.AnnoyIndex("angular")
        nn_indices = []

        # get returns
        return photograph_models.Photograph.objects.filter(id__in=nn_indices).all()

    def build_distance_matrix(self):
        """
        Take a queryset of photographs and build a distance matrix

        https://towardsdatascience.com/finding-similar-images-using-deep-learning-and-locality-sensitive-hashing-9528afee02f5

        https://pytorch.org/hub/pytorch_vision_inception_v3/
        """

        if self.photographs.count() == 0:
            Exception("Associate photographs with the current model first")

        print("Loading inception v3 model")
        model = torch.hub.load("pytorch/vision:v0.5.0", "resnet18", pretrained=True)
        print("Model downloaded. Begin eval")
        model.eval()
        print("Eval finished")
        embeddings_mat = []

        preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        newmodel = torch.nn.Conv2d(*(list(model.children())[:-1]))

        for pic in tqdm(self.photographs.all()):
            dl_path = tempfile.TemporaryFile(mode="wb")
            squared_small_path = f"{pic.iiif_base}/full/299,299/0/default.jpg"
            requests

            res = requests.get(squared_small_path)
            img = Image.open(BytesIO(res.content))

            img_array = np.repeat(np.array(img)[..., np.newaxis], 3, -1)
            # Convert to a false rgb image
            rgb_img = Image.fromarray(img_array)

            input_tensor = preprocess(rgb_img)
            input_batch = input_tensor.unsqueeze(0)

            with torch.no_grad():
                output = np.array(model(input_batch).flatten())
                print(output)
                # embeddings_mat.append(output)

        # final_path = settings.DIST_MATRICES_PATH + "/" + self.id + ".pl"
        # with open(file_path, "wb") as fl:
        #     pickle.dump(embeddings_mat, file=fl)

        # self.pickled_file = final_path
        # self.save()
