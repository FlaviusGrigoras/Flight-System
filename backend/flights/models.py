from django.db import models
from django.core.validators import MinValueValidator


class Flight(models.Model):
    airline_company = models.ForeignKey(
        "accounts.AirlineCompany", on_delete=models.CASCADE
    )
    origin_country = models.ForeignKey(
        "geo.Country", related_name="departures", on_delete=models.CASCADE
    )
    destination_country = models.ForeignKey(
        "geo.Country", related_name="arrivals", on_delete=models.CASCADE
    )

    departure_time = models.DateTimeField()
    landing_time = models.DateTimeField()
    remaining_tickets = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.airline_company.name} Flight ({self.origin_country} -> {self.destination_country})"
