from datetime import datetime

from django.db.models import Count, F
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

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
    ShowSessionListSerializer,
    AstronomyShowListSerializer,
    AstronomyShowRetrieveSerializer,
    ShowSessionRetrieveSerializer,
    ReservationCreateSerializer,
    TicketListSerializer,
    ReservationListSerializer, AstronomyShowImageSerializer,
)


class ShowThemeViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = ShowTheme.objects.all().order_by("id")
    serializer_class = ShowThemeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AstronomyShowViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = AstronomyShow.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        elif self.action == "retrieve":
            return AstronomyShowRetrieveSerializer
        elif self.action == "upload_image":
            return AstronomyShowImageSerializer
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

    @action(
        methods=["post",], detail=True, permission_classes=[IsAdminUser],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        astronomy_show = self.get_object()
        serializer = self.get_serializer(astronomy_show,
                                         data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanetariumDomeViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
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
                - Count("tickets", distinct=True)
            )
        elif self.action == "retrieve":
            queryset = queryset.select_related("astronomy_show", "planetarium_dome")
        return queryset.order_by("id")


class ReservationViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
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
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer


class TicketViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketListSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        return self.queryset.select_related("show_session", "reservation")
