from django.contrib.auth import get_user_model
from django.db import models


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=125)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()


class ShowTheme(models.Model):
    name = models.CharField(max_length=125)


class AstronomyShow(models.Model):
    title = models.CharField(max_length=125)
    description = models.TextField(max_length=500)
    theme = models.ManyToManyField(ShowTheme)


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE)
    planetarium_dome = models.ForeignKey(PlanetariumDome, on_delete=models.CASCADE)
    show_time = models.DateTimeField()


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(ShowSession, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
