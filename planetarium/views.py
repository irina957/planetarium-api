from rest_framework import viewsets
from planetarium.models import (
    ShowTheme, AstronomyShow, PlanetariumDome,
    ShowSession, Reservation, Ticket
)
from planetarium.serializers import (
    ShowThemeSerializer, AstronomyShowSerializer,
    PlanetariumDomeSerializer, ShowSessionSerializer,
    ReservationSerializer, TicketSerializer, ShowSessionListSerializer
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        return ShowSessionSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related()
        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
