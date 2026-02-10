from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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


TICKET_URL = reverse("planetarium:ticket-list")


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


class UnAuthenticatedTicketTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_tickets(self):
        show_session = sample_show_session()
        reservation = Reservation.objects.create(user=self.user)
        Ticket.objects.create(
            show_session=show_session, reservation=reservation, row=1, seat=1
        )

        res = self.client.get(TICKET_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)


class TicketModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="testpass"
        )
        self.dome = sample_planetarium_dome(rows=10, seats_in_row=15)
        self.show_session = sample_show_session(planetarium_dome=self.dome)
        self.reservation = Reservation.objects.create(user=self.user)

    def test_ticket_str(self):
        ticket = Ticket.objects.create(
            show_session=self.show_session,
            reservation=self.reservation,
            row=5,
            seat=10,
        )
        self.assertIn("Row: 5", str(ticket))

    def test_invalid_row(self):
        with self.assertRaises((ValidationError, ValueError)):
            Ticket.objects.create(
                show_session=self.show_session,
                reservation=self.reservation,
                row=99,
                seat=5,
            )

    def test_invalid_seat(self):
        with self.assertRaises((ValidationError, ValueError)):
            Ticket.objects.create(
                show_session=self.show_session,
                reservation=self.reservation,
                row=5,
                seat=99,
            )

    def test_duplicate_ticket(self):
        Ticket.objects.create(
            show_session=self.show_session,
            reservation=self.reservation,
            row=5,
            seat=10,
        )
        reservation2 = Reservation.objects.create(user=self.user)
        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                show_session=self.show_session,
                reservation=reservation2,
                row=5,
                seat=10,
            )
