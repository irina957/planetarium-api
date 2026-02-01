from datetime import datetime

from django.db.models import Count, F
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly
from planetarium.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ReservationSerializer,
    TicketSerializer,
    ShowSessionListSerializer,
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
    ShowSessionRetrieveSerializer,
    ReservationCreateSerializer,
    TicketCreateSerializer, TicketListSerializer, ReservationListSerializer,
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all().order_by("id")
    serializer_class = ShowThemeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
            try:
                theme_ids = [int(pk) for pk in themes.split(",")]
                queryset = queryset.filter(themes__id__in=theme_ids).distinct()
            except ValueError:
                raise ValidationError({"themes": "Use comma separated integers"})
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("themes")
        return queryset.order_by("id")


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all().order_by("id")
    serializer_class = PlanetariumDomeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return ShowSessionSerializer

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date", None)
        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                queryset = queryset.filter(show_time__date=date)
            except ValueError:
                raise ValidationError({"date": "Use format YYYY-MM-DD"})
        if self.action == "list":
            queryset = queryset.select_related(
                "astronomy_show", "planetarium_dome"
            ).annotate(
                tickets_available=F("planetarium_dome__rows")
                * F("planetarium_dome__seats_in_row")
                - Count("tickets")
            )
        elif self.action == "retrieve":
            queryset = queryset.select_related("astronomy_show",
                                               "planetarium_dome")
        return queryset.order_by("id")


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.prefetch_related(
            "tickets__show_session__astronomy_show",
            "tickets__show_session__planetarium_dome",
        )
        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        elif self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "create":
            return TicketCreateSerializer
        return TicketSerializer
