from datetime import datetime

from django.db.models import Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    PlanetariumDome,
    ShowSession,
    Reservation,
)
from planetarium.permissions import IsAdminOrIfAuthenticatedReadOnly
from planetarium.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    PlanetariumDomeSerializer,
    ShowSessionSerializer,
    ReservationSerializer,
    ShowSessionListSerializer, AstronomyShowListSerializer, PlanetariumDomeListSerializer, ReservationListSerializer,
    AstronomyShowDetailSerializer, ShowSessionDetailSerializer, AstronomyShowImageSerializer
)


class ShowThemeViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AstronomyShowViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = AstronomyShow.objects.prefetch_related("themes")
    serializer_class = AstronomyShowSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        if self.action == "upload_image":
            return AstronomyShowImageSerializer
        return AstronomyShowSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the astronomy show with filters"""
        title = self.request.query_params.get("title")
        themes = self.request.query_params.get("themes")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)
        if themes:
            themes_ids = self._params_to_ints(themes)
            queryset = queryset.filter(themes__id__in=themes_ids)
        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        astronomy_show = self.get_object()
        serializer = self.get_serializer(astronomy_show, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "themes",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by themes id (ex. ?themes=1,3",
            ),
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by astronomy show title (ex. ?title=mars",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of astronomy shows"""
        return super().list(request, *args, **kwargs)


class PlanetariumDomeViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PlanetariumDomeListSerializer

        return PlanetariumDomeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = (ShowSession.objects
    .select_related("astronomy_show", "planetarium_dome")
    .annotate(tickets_available=(
            F("planetarium_dome__rows")
            * F("planetarium_dome__seats_in_row")
            - Count("tickets", distinct=True)
    )
    )
    )
    serializer_class = ShowSessionSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """
        Filter show sessions by date (?date=2026-07-23)
        and/or astronomy show id (?show=1).
        """
        date = self.request.query_params.get("date")
        show_id_str = self.request.query_params.get("show")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)
        if show_id_str:
            queryset = queryset.filter(astronomy_show_id=int(show_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                type=OpenApiTypes.STR,
                description="Filter by show session date (ex. ?date=2026-07-23)"
            ),
            OpenApiParameter(
                "show",
                type=OpenApiTypes.INT,
                description="Filter by astronomy show id (ex. ?show=1)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of show sessions"""
        return super().list(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class ReservationViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    queryset = Reservation.objects
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def get_queryset(self):
        return (Reservation.objects
                .filter(user=self.request.user)
                .prefetch_related(
            "tickets__show_session__astronomy_show",
            "tickets__show_session__planetarium_dome"
        )
                )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
