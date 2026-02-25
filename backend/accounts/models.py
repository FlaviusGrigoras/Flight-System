from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    image = models.ImageField(upload_to="profiles/", null=True, blank=True)
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


class AirlineCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey("geo.Country", on_delete=models.CASCADE)
    website = models.URLField(max_length=200, null=True, blank=True)
    logo = models.ImageField(upload_to="airlines/", null=True, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="airline_profile"
    )

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_profile"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Administrator(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="admin_profile"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
