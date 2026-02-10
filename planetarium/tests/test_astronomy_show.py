import tempfile
import os
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from planetarium.models import AstronomyShow, ShowTheme
from planetarium.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")


def detail_url(astronomy_show_id):
    return reverse("planetarium:astronomyshow-detail", args=[astronomy_show_id])


def image_upload_url(astronomy_show_id):
    return reverse("planetarium:astronomyshow-upload-image", args=[astronomy_show_id])


def sample_astronomy_show(**kwargs):
    defaults = {
        "title": "Sample Astronomy Show",
        "description": "Sample Astronomy Show",
    }
    defaults.update(kwargs)
    return AstronomyShow.objects.create(**defaults)


class UnAuthenticatedAstronomyShowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_requires(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_astronomy_shows(self):
        show_with_theme = sample_astronomy_show()
        theme1 = ShowTheme.objects.create(name="test")
        theme2 = ShowTheme.objects.create(name="test2")
        show_with_theme.themes.add(theme1, theme2)

        astronomy_shows = AstronomyShow.objects.all()
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)
        res = self.client.get(ASTRONOMY_SHOW_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_astronomy_shows(self):
        show_without_theme = sample_astronomy_show()
        show_with_theme1 = sample_astronomy_show(title="Astronomy Show with theme1")
        show_with_theme2 = sample_astronomy_show(title="Astronomy Show with theme2")
        theme1 = ShowTheme.objects.create(name="test")
        theme2 = ShowTheme.objects.create(name="test2")
        show_with_theme1.themes.add(theme1)
        show_with_theme2.themes.add(theme2)

        res = self.client.get(
            ASTRONOMY_SHOW_URL, {"themes": f"{theme1.id},{theme2.id}"}
        )

        serializer_with_theme1 = AstronomyShowListSerializer(show_with_theme1)
        serializer_with_theme2 = AstronomyShowListSerializer(show_with_theme2)
        serializer_without_theme = AstronomyShowListSerializer(show_without_theme)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_with_theme1.data, res.data["results"])
        self.assertIn(serializer_with_theme2.data, res.data["results"])
        self.assertNotIn(serializer_without_theme.data, res.data["results"])

    def test_retrieve_astronomy_show(self):
        show_with_theme = sample_astronomy_show()
        show_with_theme.themes.add(ShowTheme.objects.create(name="test theme"))

        url = detail_url(show_with_theme.id)
        res = self.client.get(url)

        serializer = AstronomyShowRetrieveSerializer(show_with_theme)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_astronomy_show_forbidden(self):
        payload = {
            "title": "Sample Astronomy Show",
            "description": "Sample Astronomy Show",
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="testpassword", is_staff=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_astronomy_show(self):
        payload = {
            "title": "Sample Astronomy Show",
            "description": "Sample Astronomy Show",
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        show = AstronomyShow.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(show, key))

    def test_create_astronomy_show_with_themes(self):
        theme1 = ShowTheme.objects.create(name="test")
        theme2 = ShowTheme.objects.create(name="test2")
        payload = {
            "title": "Sample Astronomy Show",
            "description": "Sample Astronomy Show",
            "themes": [theme1.id, theme2.id],
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        show = AstronomyShow.objects.get(id=res.data["id"])
        themes = show.themes.all()
        self.assertIn(theme1, themes)
        self.assertIn(theme2, themes)
        self.assertEqual(themes.count(), 2)
        self.assertEqual(len(res.data["themes"]), 2)

    def test_delete_astronomy_show_not_allowed(self):
        show = sample_astronomy_show()
        url = detail_url(show.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AstronomyShowImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)
        self.astronomy_show = sample_astronomy_show()

    def tearDown(self):
        if self.astronomy_show.image:
            self.astronomy_show.image.delete()

    def test_upload_image_to_astronomy_show(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.astronomy_show.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.astronomy_show.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.astronomy_show.id)
        res = self.client.post(url, {"image": "not an image"}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_to_astronomy_show_list_not_allowed(self):
        url = ASTRONOMY_SHOW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "New Show",
                    "description": "New Description",
                    "image": ntf,
                },
                format="multipart",
            )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(title="New Show")
        self.assertFalse(astronomy_show.image)

    def test_image_url_is_shown_on_astronomy_show_detail(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        res = self.client.get(detail_url(self.astronomy_show.id))
        self.assertIn("image", res.data)
        self.assertIsNotNone(res.data["image"])

    def test_image_url_is_shown_on_astronomy_show_list(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertIn("image", res.data["results"][0].keys())
        self.assertIsNotNone(res.data["results"][0]["image"])

    def test_upload_image_unauthorized(self):
        regular_user = get_user_model().objects.create_user(
            email="regular@test.com", password="testpassword"
        )
        self.client.force_authenticate(regular_user)
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_to_nonexistent_astronomy_show(self):
        url = image_upload_url(9999)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_replace_existing_image(self):
        url = image_upload_url(self.astronomy_show.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (20, 20))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.astronomy_show.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(os.path.exists(self.astronomy_show.image.path))
