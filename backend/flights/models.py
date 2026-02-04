from django.db import models
from django.core.validators import MinValueValidator


class Flight(models.Model):
    airline_company = models.ForeignKey(
        "accounts.AirlineCompany", on_delete=models.PROTECT, related_name="flights"
    )
    origin_airport = models.ForeignKey(
        "geo.Airport",
        on_delete=models.PROTECT,
        related_name="departing_flights",
        null=True,
        blank=True,
    )
    destination_airport = models.ForeignKey(
        "geo.Airport",
        on_delete=models.PROTECT,
        related_name="arriving_flights",
        null=True,
        blank=True,
    )

    departure_time = models.DateTimeField()
    landing_time = models.DateTimeField()
    remaining_tickets = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        origin = self.origin_airport or "N/A"
        destination = self.destination_airport or "N/A"
        return f"{self.airline_company.name} Flight ({origin} -> {destination})"
