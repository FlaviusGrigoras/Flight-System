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
    economy_seats = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    business_seats = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    remaining_economy_tickets = models.IntegerField(
        validators=[MinValueValidator(0)], default=0
    )
    remaining_business_tickets = models.IntegerField(
        validators=[MinValueValidator(0)], default=0
    )
    economy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    business_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        origin = self.origin_airport or "N/A"
        destination = self.destination_airport or "N/A"
        return f"{self.airline_company.name} Flight ({origin} -> {destination})"
