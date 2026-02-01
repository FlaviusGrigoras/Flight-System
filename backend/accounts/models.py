from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser


class UserRole(models.Model):
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name


class Country(models.Model):
    # ID automat din django
    name = models.CharField(max_length=100, unique=True)
    flag_image = models.ImageField(upload_to="flags/", null=True, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    user_role = models.ForeignKey(
        UserRole, on_delete=models.CASCADE, null=True, blank=True
    )
    image = models.ImageField(upload_to="profiles/", null=True, blank=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


class AirlineCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    phone_no = models.CharField(max_length=15, unique=True)
    credit_card_no = models.CharField(max_length=13, unique=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Administrator(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    airline_company = models.ForeignKey(AirlineCompany, on_delete=models.CASCADE)
    origin_country = models.ForeignKey(
        Country, related_name="departures", on_delete=models.CASCADE
    )
    destination_country = models.ForeignKey(
        Country, related_name="arrivals", on_delete=models.CASCADE
    )

    departure_time = models.DateTimeField()
    landing_time = models.DateTimeField()

    remaining_tickets = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.airline_company.name} Flight"


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("flight", "customer")

    def __str__(self):
        return f"Ticket: {self.flight} - {self.customer}"
