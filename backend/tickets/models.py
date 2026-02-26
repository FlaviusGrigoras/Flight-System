from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CANCELLED = "CANCELLED", "Cancelled"

    class CabinClass(models.TextChoices):
        ECONOMY = "ECONOMY", "Economy"
        BUSINESS = "BUSINESS", "Business"

    flight = models.ForeignKey("flights.Flight", on_delete=models.CASCADE)
    customer = models.ForeignKey("accounts.Customer", on_delete=models.CASCADE)

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    cabin_class = models.CharField(
        max_length=16, choices=CabinClass.choices, default=CabinClass.ECONOMY
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    seat_no = models.CharField(max_length=8, blank=True, default="")

    def __str__(self):
        return f"Ticket: {self.flight} - {self.customer}"
