from datetime import timedelta
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
    Reservation,
    Ticket,
)

RESERVATION_URL = reverse("planetarium:reservation-list")


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


class UnAuthenticatedReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_reservations(self):
        # Create reservation for current user
        show_session = sample_show_session()
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            show_session=show_session, reservation=reservation, row=1, seat=1
        )

        # Create reservation for another user
        other_user = get_user_model().objects.create_user(
            email="other@test.com", password="testpass"
        )
        other_reservation = Reservation.objects.create(user=other_user)

        res = self.client.get(RESERVATION_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], reservation.id)

    def test_create_reservation(self):
        show_session = sample_show_session()
        payload = {
            "tickets": [
                {"show_session": show_session.id, "row": 1, "seat": 1},
                {"show_session": show_session.id, "row": 1, "seat": 2},
            ]
        }
        res = self.client.post(RESERVATION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        reservation = Reservation.objects.get(id=res.data["id"])
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.tickets.count(), 2)

    def test_create_reservation_empty_tickets(self):
        payload = {"tickets": []}
        res = self.client.post(RESERVATION_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reservation_str(self):
        reservation = Reservation.objects.create(user=self.user)

        self.assertIn(str(reservation.id), str(reservation))
        self.assertIn(self.user.email, str(reservation))
