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
            "height",
            "width",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
            "decisions",
        ]:
            self.assertIn(k, res.data["results"][0])
        self.assertIn("full", res.data["results"][0]["image"])
        self.assertIn("id", res.data["results"][0]["directory"])
        self.assertIn("id", res.data["results"][0]["photograph_tags"][0])

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
            "height",
            "width",
            "date_taken_early",
            "date_taken_late",
            "digitized_date",
            "directory",
            "job",
            "job_sequence",
            "photograph_tags",
            "decisions",
        ]:
            self.assertIn(k, res.data)
        self.assertIn("full", res.data["image"])
        self.assertIn("id", res.data["directory"])

    @as_auth()
    def test_filter_directory(self):
        dir_id = models.Photograph.objects.first().directory.id
        res = self.client.get(self.ENDPOINT, data={"directory": dir_id})
        self.assertEqual(res.status_code, 200)
        for p in res.data["results"]:
            self.assertTrue(p["directory"]["id"] == dir_id)

    @as_auth()
    def test_filter_job(self):
        job_id = models.Photograph.objects.filter(job__isnull=False).first().job.id
        res = self.client.get(self.ENDPOINT, data={"job": job_id})
        self.assertEqual(res.status_code, 200)
        for p in res.data["results"]:
            self.assertTrue(p["job"]["id"] == job_id)

    @as_auth()
    def test_filter_job_tag(self):
        job_tag = (
            models.Photograph.objects.filter(job__isnull=False).first().job.tags.first()
        )
        res = self.client.get(self.ENDPOINT, data={"job_tag": job_tag.id})
        self.assertEqual(res.status_code, 200)
        for p in res.data["results"]:
            self.assertEqual(job_tag.jobs.first().id, p["job"]["id"])

    @as_auth()
    def test_filter_image_path(self):
        pathstring = models.Photograph.objects.first().image_path
        res = self.client.get(self.ENDPOINT, data={"image_path": pathstring})
        self.assertEqual(res.status_code, 200)
        for p in res.data["results"]:
            self.assertIn(p["filename"], pathstring)

    @as_auth()
    def test_filter_tag(self):
        tag = (
            models.Photograph.objects.filter(photograph_tags__isnull=False)
            .first()
            .photograph_tags.first()
            .tag
        )
        res = self.client.get(self.ENDPOINT, data={"tag": tag.id})
        self.assertEqual(res.status_code, 200)
        for p in res.data["results"]:
            self.assertIn(tag.id, [t["tag"]["id"] for t in p["photograph_tags"]])

