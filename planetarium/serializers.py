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
        fields = ("id", "title", "description")


class AstronomyShowListSerializer(AstronomyShowSerializer):
        show_theme = serializers.SlugRelatedField(many=True, read_only=True, slug_field="theme.name")

        class Meta:
            model = AstronomyShow
            fields = ("id", "title", "description", "show_theme")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row")


class PlanetariumDomeListSerializer(PlanetariumDomeSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")


class ShowSessionListSerializer(ShowSessionSerializer):
    show_title = serializers.CharField(source="astronomy_show.title")
    planetarium_dome_name = serializers.CharField(source="planetarium_dome.name")
    planetarium_dome_capacity = serializers.IntegerField(source="planetarium_dome.capacity")
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShowSession
        fields = ("id", "show_time", "show_title", "planetarium_dome_name", "planetarium_dome_capacity", "tickets_available")



class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")


class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(many=False, read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        reservation = Reservation.objects.create(**validated_data)
        for ticket in tickets_data:
            Ticket.objects.create(reservation=reservation, **ticket)
        return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
