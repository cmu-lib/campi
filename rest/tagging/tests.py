from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from campi.tests import noaccess, as_auth
from tagging import models
import photograph.models


class TagListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("tag-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.Tag.objects.first()
        cls.OBJ2 = models.Tag.objects.last()

    def test_noaccess(self):
        noaccess(self)

    @as_auth()
    def test_get(self):
        res = self.client.get(self.ENDPOINT)
        self.assertEqual(res.status_code, 200)
        for k in ["id", "label", "n_images", "tasks"]:
            self.assertIn(k, res.data["results"][0])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual(res.status_code, 200)
        for k in ["id", "label", "n_images", "tasks"]:
            self.assertIn(k, res.data)

    @as_auth()
    def test_post(self):
        bad_res = self.client.post(f"{self.ENDPOINT}", {"label": self.OBJ1.label})
        self.assertEqual(bad_res.status_code, 400)
        res = self.client.post(f"{self.ENDPOINT}", {"label": "foo"})
        for k in ["id", "label", "tasks"]:
            self.assertIn(k, res.data)
        self.assertEqual("foo", res.data["label"])

    @as_auth()
    def test_patch(self):
        bad_res = self.client.patch(
            f"{self.ENDPOINT}{self.OBJ1.id}/", {"label": self.OBJ2.label}
        )
        self.assertEqual(bad_res.status_code, 400)
        res = self.client.patch(f"{self.ENDPOINT}{self.OBJ1.id}/", {"label": "foo"})
        for k in ["id", "label", "tasks"]:
            self.assertIn(k, res.data)
        self.assertEquals("foo", res.data["label"])

    @as_auth()
    def test_label_filter(self):
        res = self.client.get(self.ENDPOINT, data={"label": self.OBJ1.label})
        self.assertEqual(res.status_code, 200)
        for tag in res.data["results"]:
            self.assertIn(self.OBJ1.label.lower(), tag["label"].lower())

    @as_auth()
    def test_job_filter(self):
        target_job = self.OBJ1.photograph_tags.first().photograph.job
        res = self.client.get(self.ENDPOINT, data={"job": target_job.id})
        self.assertEqual(res.status_code, 200)
        for tag in res.data["results"]:
            self.assertTrue(
                photograph.models.Photograph.objects.filter(
                    photograph_tags__tag=tag["id"], job=target_job
                ).exists()
            )

    @as_auth()
    def test_job_tag_filter(self):
        target_job_tag = self.OBJ1.photograph_tags.first().photograph.job.tags.first()
        res = self.client.get(self.ENDPOINT, data={"job_tag": target_job_tag.id})
        self.assertEqual(res.status_code, 200)
        for tag in res.data["results"]:
            self.assertTrue(
                photograph.models.Photograph.objects.filter(
                    photograph_tags__tag=tag["id"], job__tags=target_job_tag
                ).exists()
            )


class TaggingTaskListView(TestCase):
    fixtures = ["campi/fixtures/test.json"]

    ENDPOINT = reverse("taggingtask-list")

    @classmethod
    def setUpTestData(cls):
        cls.OBJ1 = models.TaggingTask.objects.first()
        cls.OBJ2 = models.TaggingTask.objects.last()

    def test_noaccess(self):
        noaccess(self)

    @as_auth()
    def test_get(self):
        res = self.client.get(self.ENDPOINT)
        self.assertEqual(res.status_code, 200)
        for k in ["id", "tag", "pytorch_model", "assigned_user"]:
            self.assertIn(k, res.data["results"][0])
        self.assertIn("label", res.data["results"][0]["tag"])

    @as_auth()
    def test_get_detail(self):
        res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual(res.status_code, 200)
        for k in ["id", "tag", "pytorch_model", "assigned_user"]:
            self.assertIn(k, res.data)
        self.assertIn("label", res.data["tag"])

    @as_auth()
    def test_post(self):
        bad_res = self.client.post(
            f"{self.ENDPOINT}",
            {"tag": self.OBJ1.tag.id, "pytorch_model": self.OBJ1.pytorch_model.id},
        )
        self.assertEqual(bad_res.status_code, 400)
        newtask = models.Tag.objects.filter(tasks__isnull=True).first()
        res = self.client.post(
            f"{self.ENDPOINT}",
            {"tag": newtask.id, "pytorch_model": self.OBJ1.pytorch_model.id},
        )
        for k in ["id", "tag", "pytorch_model"]:
            self.assertIn(k, res.data)
        new_task_res = self.client.get(f"{self.ENDPOINT}{res.data['id']}/")
        self.assertEqual("root", new_task_res.data["assigned_user"]["username"])

    @as_auth()
    def test_patch(self):
        res = self.client.put(
            f"{self.ENDPOINT}{self.OBJ1.id}/",
            {"tag": self.OBJ1.tag.id, "pytorch_model": self.OBJ1.pytorch_model.id},
        )
        self.assertEqual(res.status_code, 200)
        put_res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual("root", put_res.data["assigned_user"]["username"])

    @as_auth("bob")
    def test_new_patch(self):
        res = self.client.put(
            f"{self.ENDPOINT}{self.OBJ1.id}/",
            {"tag": self.OBJ1.tag.id, "pytorch_model": self.OBJ1.pytorch_model.id},
        )
        self.assertEqual(res.status_code, 200)
        put_res = self.client.get(f"{self.ENDPOINT}{self.OBJ1.id}/")
        self.assertEqual("bob", put_res.data["assigned_user"]["username"])
