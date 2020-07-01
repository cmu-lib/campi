from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from campi.tests import noaccess, as_auth
from photograph import models


class PhotographListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("photograph-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.Photograph.objects.first().id

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
            "url",
            "id",
            "label",
            "image",
            "filename",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
        ]:
            self.assertIn(k, res.data["results"][0])
        self.assertIn("full", res.data["results"][0]["image"])
        self.assertIn("id", res.data["results"][0]["directory"])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1}/")
        self.assertEqual(res.status_code, 200)
        for k in [
            "url",
            "id",
            "label",
            "image",
            "filename",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
        ]:
            self.assertIn(k, res.data)
        self.assertIn("full", res.data["image"])
        self.assertIn("id", res.data["directory"])
