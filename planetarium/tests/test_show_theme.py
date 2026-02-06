from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from planetarium.models import ShowTheme


SHOW_THEME_URL = reverse("planetarium:showtheme-list")


class UnAuthenticatedShowThemeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_THEME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedShowThemeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_show_themes(self):
        ShowTheme.objects.create(name="Space")
        ShowTheme.objects.create(name="Planets")

        res = self.client.get(SHOW_THEME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_create_show_theme_forbidden(self):
        payload = {"name": "Stars"}
        res = self.client.post(SHOW_THEME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowThemeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_show_theme(self):
        payload = {"name": "Galaxies"}
        res = self.client.post(SHOW_THEME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ShowTheme.objects.filter(name="Galaxies").exists())

    def test_show_theme_str(self):
        theme = ShowTheme.objects.create(name="Stars")
        self.assertEqual(str(theme), "Stars")
