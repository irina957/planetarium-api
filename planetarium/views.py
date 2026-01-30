from datetime import datetime

from rest_framework import viewsets
from planetarium.models import (
    ShowTheme, AstronomyShow, PlanetariumDome,
    ShowSession, Reservation, Ticket
)
from planetarium.serializers import (
    ShowThemeSerializer, AstronomyShowSerializer,
    PlanetariumDomeSerializer, ShowSessionSerializer,
    ReservationSerializer, TicketSerializer,
    ShowSessionListSerializer, AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer, ShowSessionRetrieveSerializer
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        elif self.action == "retrieve":
            return AstronomyShowRetrieveSerializer
        return AstronomyShowSerializer

    def get_queryset(self):
        queryset = self.queryset
        themes = self.request.query_params.get("themes", None)
        if themes:
            themes_ids = [int(str_id) for str_id in themes.split(",")]
            queryset = queryset.filter(themes__id__in=themes_ids).distinct()
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("themes")
        return queryset


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return ShowSessionSerializer

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date", None)
        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)
        if self.action in ("list", "retrieve"):
            return queryset.select_related("astronomy_show",
                                           "planetarium_dome")
        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
