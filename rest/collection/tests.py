from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from campi.tests import noaccess, as_auth
from collection import models
import photograph


class DirectoryListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("directory-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.Directory.objects.exclude(
            immediate_photographs__job__isnull=True
        ).first()
        cls.OBJ2 = models.Directory.objects.exclude(
            immediate_photographs__photograph_tags__isnull=True
        ).first()

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
        for k in ["url", "id", "label", "description", "n_images", "parent_directory"]:
            self.assertIn(k, res.data[0])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual(res.status_code, 200)
        for k in [
            "url",
            "id",
            "label",
            "description",
            "n_images",
            "parent_directory",
            "child_directories",
        ]:
            self.assertIn(k, res.data)
        self.assertIsInstance(res.data["child_directories"], list)

    @as_auth()
    def test_label_filter(self):
        res = self.client.get(self.ENDPOINT, data={"label": self.OBJ1.label})
        self.assertEqual(res.status_code, 200)
        for d in res.data:
            self.assertIn(self.OBJ1.label.lower(), d["label"].lower())

    @as_auth()
    def test_job_filter(self):
        target_job = self.OBJ1.immediate_photographs.first().job
        res = self.client.get(self.ENDPOINT, data={"job": target_job.id})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(
            any(
                [
                    any(
                        [
                            p.job.id == target_job.id
                            for p in photograph.models.Photograph.objects.filter(
                                directory__id=directory["id"], job__isnull=False
                            )
                        ]
                    )
                    for directory in res.data
                ]
            )
        )

    @as_auth()
    def test_job_tag_filter(self):
        target_job = self.OBJ1.immediate_photographs.first().job
        res = self.client.get(
            self.ENDPOINT, data={"job_tag": target_job.tags.first().id}
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(
            any(
                [
                    any(
                        [
                            p.job.id == target_job.id
                            for p in photograph.models.Photograph.objects.filter(
                                directory__id=directory["id"], job__isnull=False
                            )
                        ]
                    )
                    for directory in res.data
                ]
            )
        )

    @as_auth()
    def test_tag_filter(self):
        target_tag = (
            self.OBJ2.immediate_photographs.filter(photograph_tags__isnull=False)
            .first()
            .photograph_tags.first()
            .tag
        )
        res = self.client.get(self.ENDPOINT, data={"tag": target_tag.id})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(
            any(
                [
                    any(
                        [
                            p.job.id == target_job.id
                            for p in photograph.models.Photograph.objects.filter(
                                directory__id=directory["id"],
                                photograph_tags__isnull=False,
                            )
                        ]
                    )
                    for directory in res.data
                ]
            )
        )


class JobListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("job-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.Job.objects.first()

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
            "description",
            "n_images",
            "job_code",
            "date_start",
            "date_end",
        ]:
            self.assertIn(k, res.data["results"][0])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual(res.status_code, 200)
        for k in [
            "url",
            "id",
            "label",
            "description",
            "n_images",
            "job_code",
            "date_start",
            "date_end",
        ]:
            self.assertIn(k, res.data)

    @as_auth()
    def test_text_filter(self):
        res = self.client.get(self.ENDPOINT, data={"text": self.OBJ1.label})
        self.assertEqual(res.status_code, 200)
        for d in res.data["results"]:
            self.assertIn(self.OBJ1.label.lower(), d["label"].lower())

    @as_auth()
    def test_job_tag_filter(self):
        job_tag = self.OBJ1.tags.first()
        res = self.client.get(self.ENDPOINT, data={"job_tag": job_tag.id})
        self.assertEqual(res.status_code, 200)
        for d in res.data["results"]:
            self.assertIn(job_tag.label.lower(), d["label"].lower())

    @as_auth()
    def test_directory_filter(self):
        directory = self.OBJ1.photographs.first().directory
        res = self.client.get(self.ENDPOINT, data={"direcotry": directory.id})
        self.assertEqual(res.status_code, 200)
        self.assertIn(self.OBJ1.id, [d["id"] for d in res.data["results"]])

    @as_auth()
    def test_tag_filter(self):
        tag = (
            models.Job.objects.filter(photographs__photograph_tags__isnull=False)
            .first()
            .photographs.first()
            .photograph_tags.first()
            .tag
        )
        res = self.client.get(self.ENDPOINT, data={"tag": tag.id})
        self.assertEqual(res.status_code, 200)
        for d in res.data["results"]:
            self.assertTrue(
                any(
                    [
                        tag.id in [t.tag.id for t in p.photograph_tags.all()]
                        for p in photograph.models.Photograph.objects.filter(
                            job__id=d["id"]
                        ).all()
                    ]
                )
            )

