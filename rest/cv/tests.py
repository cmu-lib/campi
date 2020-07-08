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


class CloseMatchSetListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("closematchset-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.CloseMatchSet.objects.first()

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
            "close_match_run",
            "representative_photograph",
            "memberships",
            "user_last_modified",
            "last_updated",
            "has_duplicates",
            "n_images",
            "n_unreviewed_images",
            "n_redundant_images",
            "overlapping",
            "redundant",
        ]:
            self.assertIn(k, res.data["results"][0])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual(res.status_code, 200)
        for k in [
            "id",
            "close_match_run",
            "representative_photograph",
            "memberships",
            "user_last_modified",
            "last_updated",
            "has_duplicates",
            "n_images",
            "n_unreviewed_images",
            "n_redundant_images",
            "overlapping",
            "redundant",
        ]:
            self.assertIn(k, res.data)

    @as_auth()
    def test_filter_close_match_run(self):
        cmr = self.OBJ1.close_match_run
        res = self.client.get(f"{self.ENDPOINT}", {"close_match_run": cmr.id})
        self.assertEqual(res.status_code, 200)
        for s in res.data["results"]:
            self.assertEqual(cmr.id, s["close_match_run"]["id"])

    @as_auth()
    def test_redundant(self):
        res = self.client.get(f"{self.ENDPOINT}", {"redundant": True})
        self.assertEqual(res.status_code, 200)
        for s in res.data["results"]:
            self.assertTrue(s["redundant"])

    @as_auth()
    def test_overlapping(self):
        res = self.client.get(f"{self.ENDPOINT}", {"overlapping": True})
        self.assertEqual(res.status_code, 200)
        for s in res.data["results"]:
            self.assertTrue(s["overlapping"])

    @as_auth()
    def test_user_signed_off(self):
        res = self.client.get(f"{self.ENDPOINT}", {"unreviewed": True})
        self.assertEqual(res.status_code, 200)
        for s in res.data["results"]:
            self.assertIsNone(s["user_last_modified"])

    @as_auth()
    def test_memberships(self):
        photo = self.OBJ1.memberships.first().photograph
        res = self.client.get(f"{self.ENDPOINT}", {"memberships": photo.id})
        self.assertEqual(res.status_code, 200)
        for s in res.data["results"]:
            self.assertIn(photo.id, [m["photograph"]["id"] for m in s["memberships"]])
