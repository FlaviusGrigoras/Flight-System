from django.db import models


class Ticket(models.Model):
    flight = models.ForeignKey("flights.Flight", on_delete=models.CASCADE)
    customer = models.ForeignKey("accounts.Customer", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("flight", "customer")

    def __str__(self):
        return f"Ticket: {self.flight} - {self.customer}"
