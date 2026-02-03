from django.db import transaction
from rest_framework import serializers

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "description", "themes", "image")


class AstronomyShowImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "image")


class AstronomyShowListSerializer(AstronomyShowSerializer):
    themes = serializers.SlugRelatedField(many=True, read_only=True,
                                          slug_field="name")


class AstronomyShowRetrieveSerializer(AstronomyShowSerializer):
    themes = ShowThemeSerializer(many=True, read_only=True)


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row")


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show_title = serializers.CharField(
        source="astronomy_show.title", read_only=True
    )
    planetarium_dome_name = serializers.CharField(
        source="planetarium_dome.name", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True,)

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show_title",
                  "planetarium_dome_name", "show_time", "tickets_available")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session", "reservation")

    def validate(self, attrs):
        Ticket.validate_row(attrs["row"],
                            attrs["show_session"].planetarium_dome.rows,
                            serializers.ValidationError)
        Ticket.validate_seat(attrs["seat"],
                             attrs["show_session"].planetarium_dome.seats_in_row,
                             serializers.ValidationError)
        return attrs

class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(many=False, read_only=True)

class TicketBriefSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat",)


class ShowSessionRetrieveSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowRetrieveSerializer(many=False,
                                                     read_only=True)
    planetarium_dome = PlanetariumDomeSerializer(many=False, read_only=True)
    taken_seats = TicketBriefSerializer(source="tickets",
                                        many=True, read_only=True)

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show",
                  "planetarium_dome", "show_time", "taken_seats")


class TicketCreateSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat", "show_session")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

class ReservationCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation
