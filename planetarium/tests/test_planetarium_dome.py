from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from planetarium.models import PlanetariumDome


PLANETARIUM_DOME_URL = reverse("planetarium:planetariumdome-list")


class UnAuthenticatedPlanetariumDomeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLANETARIUM_DOME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlanetariumDomeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_planetarium_domes(self):
        PlanetariumDome.objects.create(name="Dome 1", rows=10, seats_in_row=15)
        PlanetariumDome.objects.create(name="Dome 2", rows=12, seats_in_row=20)

        res = self.client.get(PLANETARIUM_DOME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_create_planetarium_dome_forbidden(self):
        payload = {"name": "Dome 3", "rows": 8, "seats_in_row": 10}
        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlanetariumDomeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_planetarium_dome(self):
        payload = {"name": "Large Dome", "rows": 15, "seats_in_row": 25}
        res = self.client.post(PLANETARIUM_DOME_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PlanetariumDome.objects.filter(name="Large Dome").exists())

    def test_planetarium_dome_str(self):
        dome = PlanetariumDome.objects.create(
            name="Test Dome", rows=10, seats_in_row=12
        )
        self.assertEqual(str(dome), "Test Dome")
