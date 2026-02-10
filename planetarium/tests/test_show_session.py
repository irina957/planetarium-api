from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from planetarium.models import (
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
)

SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def detail_url(show_session_id):
    return reverse("planetarium:showsession-detail", args=[show_session_id])


def sample_astronomy_show(**kwargs):
    defaults = {"title": "Sample Show", "description": "Sample Description"}
    defaults.update(kwargs)
    return AstronomyShow.objects.create(**defaults)


def sample_planetarium_dome(**kwargs):
    defaults = {"name": "Dome 1", "rows": 10, "seats_in_row": 15}
    defaults.update(kwargs)
    return PlanetariumDome.objects.create(**defaults)


def sample_show_session(**kwargs):
    astronomy_show = sample_astronomy_show()
    planetarium_dome = sample_planetarium_dome()
    defaults = {
        "astronomy_show": astronomy_show,
        "planetarium_dome": planetarium_dome,
        "show_time": timezone.now() + timedelta(days=1),
    }
    defaults.update(kwargs)
    return ShowSession.objects.create(**defaults)


class UnAuthenticatedShowSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedShowSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_show_sessions(self):
        sample_show_session()
        sample_show_session()

        res = self.client.get(SHOW_SESSION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
        self.assertIn("tickets_available", res.data["results"][0])

    def test_filter_show_sessions_by_date(self):
        show_time_1 = timezone.now() + timedelta(days=1)
        show_time_2 = timezone.now() + timedelta(days=2)

        sample_show_session(show_time=show_time_1)
        sample_show_session(show_time=show_time_2)

        date_filter = show_time_1.strftime("%Y-%m-%d")
        res = self.client.get(SHOW_SESSION_URL, {"date": date_filter})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_filter_show_sessions_invalid_date_format(self):
        res = self.client.get(SHOW_SESSION_URL, {"date": "invalid-date"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", res.data)

    def test_retrieve_show_session(self):
        show_session = sample_show_session()
        url = detail_url(show_session.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], show_session.id)

    def test_create_show_session_forbidden(self):
        astronomy_show = sample_astronomy_show()
        planetarium_dome = sample_planetarium_dome()
        payload = {
            "astronomy_show": astronomy_show.id,
            "planetarium_dome": planetarium_dome.id,
            "show_time": (timezone.now() + timedelta(days=1)).isoformat(),
        }
        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowSessionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_show_session(self):
        astronomy_show = sample_astronomy_show()
        planetarium_dome = sample_planetarium_dome()
        payload = {
            "astronomy_show": astronomy_show.id,
            "planetarium_dome": planetarium_dome.id,
            "show_time": (timezone.now() + timedelta(days=1)).isoformat(),
        }
        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ShowSession.objects.filter(id=res.data["id"]).exists())

    def test_delete_show_session(self):
        show_session = sample_show_session()
        url = detail_url(show_session.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ShowSession.objects.filter(id=show_session.id).exists())

    def test_show_session_str(self):
        astronomy_show = sample_astronomy_show(title="Space Tour")
        show_time = timezone.now() + timedelta(days=1)
        show_session = sample_show_session(
            astronomy_show=astronomy_show, show_time=show_time
        )

        self.assertIn("Space Tour", str(show_session))
