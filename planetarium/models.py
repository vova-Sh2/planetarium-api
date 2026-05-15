from django.contrib.auth import get_user_model
from django.db import models


class ShowTheme(models.Model):
    name = models.CharField(max_length=125)

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=125)
    description = models.TextField(max_length=500)
    theme = models.ManyToManyField(ShowTheme, related_name="shows")

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=125)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE, related_name="shows_sessions")
    planetarium_dome = models.ForeignKey(PlanetariumDome, on_delete=models.CASCADE, related_name="shows_sessions")
    show_time = models.DateTimeField()
    def __str__(self):
        return f"{self.astronomy_show.title} - {self.planetarium_dome.name}"


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

    def __str__(self):
        return f"{self.row} - {self.seat}"
