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

