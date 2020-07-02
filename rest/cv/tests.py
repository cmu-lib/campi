from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from campi.tests import noaccess, as_auth
from cv import models
import photograph.models


class PyTorchModelListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("pytorchmodel-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.PyTorchModel.objects.first()

    @as_auth()
    def test_get(self):
        res = self.client.get(self.ENDPOINT)
        self.assertEqual(res.status_code, 200)

    def test_noaccess(self):
        noaccess(self)

    @as_auth()
    def test_get(self):
        res = self.client.get(self.ENDPOINT)
        self.assertEqual(res.status_code, 200)
        for k in ["id", "url", "label", "n_dimensions", "feature_matrix"]:
            self.assertIn(k, res.data["results"][0])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual(res.status_code, 200)
        for k in ["id", "url", "label", "n_dimensions", "feature_matrix"]:
            self.assertIn(k, res.data)

    @as_auth()
    def test_get_embeddings(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/feature_matrix/")
        self.assertEqual(res.status_code, 200)

    @as_auth()
    def test_get_nn(self):
        photo = photograph.models.Photograph.objects.first()
        res = self.client.post(
            f"{self.ENDPOINT}{self.OBJ1.id}/get_nn/",
            {"photograph": photo.id, "n_neighbors": 5},
        )
        self.assertEqual(res.status_code, 200)
        for k in [
            "id",
            "url",
            "label",
            "image",
            "filename",
            "height",
            "width",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
            "distance",
        ]:
            self.assertIn(k, res.data[0])


class CloseMatchRunListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("closematchrun-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.CloseMatchRun.objects.first()

    @as_auth()
    def test_get(self):
        res = self.client.get(self.ENDPOINT)
        self.assertEqual(res.status_code, 200)

    def test_noaccess(self):
        noaccess(self)

    @as_auth()
    def test_get(self):
        res = self.client.get(self.ENDPOINT)
        self.assertEqual(res.status_code, 200)
        for k in [
            "id",
            "url",
            "created_on",
            "pytorch_model",
            "cutoff_distance",
            "exclude_future_distance",
            "min_samples",
            "n_sets",
            "n_complete",
            "download_matches",
        ]:
            self.assertIn(k, res.data["results"][0])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual(res.status_code, 200)
        for k in [
            "id",
            "url",
            "created_on",
            "pytorch_model",
            "cutoff_distance",
            "exclude_future_distance",
            "min_samples",
            "n_sets",
            "n_complete",
            "download_matches",
        ]:
            self.assertIn(k, res.data)

    @as_auth()
    def test_download_matches(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/download_matches/")
        self.assertEqual(res.status_code, 200)
