from django.db import models
from django.conf import settings


class ShowTheme(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AstronomyShow(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    themes = models.ManyToManyField(ShowTheme, related_name="astronomy_shows")

    def __str__(self):
        return self.title


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE)
    planetarium_dome = models.ForeignKey(PlanetariumDome,
                                         on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.astronomy_show.title} at {self.show_time}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        return f"Reservation {self.id} by {self.user.get_username()}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(ShowSession,
                                     on_delete=models.CASCADE,
                                     related_name="tickets")
    reservation = models.ForeignKey(Reservation,
                                    on_delete=models.CASCADE,
                                    related_name="tickets")

    class Meta:
        unique_together = ("row", "seat", "show_session")
        ordering = ["row", "seat"]

    def __str__(self):
        return f"Ticket {self.id} (Row {self.row}, Seat {self.seat})"
