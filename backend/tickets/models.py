from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CANCELLED = "CANCELLED", "Cancelled"

    flight = models.ForeignKey("flights.Flight", on_delete=models.CASCADE)
    customer = models.ForeignKey("accounts.Customer", on_delete=models.CASCADE)

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    seat_no = models.CharField(max_length=8, blank=True, default="")

    class Meta:
        unique_together = ("flight", "customer")

    def __str__(self):
        return f"Ticket: {self.flight} - {self.customer}"
