import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.core import exceptions
from django.template.defaultfilters import slugify


class ShowTheme(models.Model):
    name = models.CharField(max_length=125)

    def __str__(self):
        return self.name


def movie_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/astronomy_show/", filename)


class AstronomyShow(models.Model):
    title = models.CharField(max_length=125)
    description = models.TextField(max_length=500)
    themes = models.ManyToManyField(ShowTheme, related_name="shows")
    poster_image = models.ImageField(upload_to=movie_image_file_path, null=True)

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=125)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE, related_name="shows_sessions")
    planetarium_dome = models.ForeignKey(PlanetariumDome, on_delete=models.CASCADE, related_name="shows_sessions")
    show_time = models.DateTimeField()
    def __str__(self):
        return f"{self.astronomy_show.title} - {self.planetarium_dome.name}"

    class Meta:
        unique_together = ("astronomy_show", "planetarium_dome", "show_time")


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="reservations")

    def __str__(self):
        return f"{self.user} - {self.created_at}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE, related_name="tickets")
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(row, seat, hall, error=exceptions.ValidationError):
        rules = [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]

        for value, field_name, attr_name in rules:
            max_value = getattr(hall, attr_name)

            if not (1 <= value <= max_value):
                raise error(
                    {
                        field_name: (
                            f"{field_name} must be between 1 and {max_value}"
                        )
                    }
                )

    def clean(self):
        Ticket.validate_ticket(self.row, self.seat, self.show_session.planetarium_dome)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.row} - {self.seat}"

    class Meta:
        unique_together = ("show_session","row", "seat")
