from django.db.models import Count, F, ExpressionWrapper, IntegerField
from rest_framework import viewsets

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
)
from planetarium.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ReservationSerializer,
    ShowSessionListSerializer, AstronomyShowListSerializer, PlanetariumDomeListSerializer, ReservationListSerializer
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        return AstronomyShowSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlanetariumDomeListSerializer

        return PlanetariumDomeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    def get_queryset(self):
        return ShowSession.objects.annotate(
            tickets_available=(
                F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
                - Count("tickets")
            )
        )



    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        return ShowSessionSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
