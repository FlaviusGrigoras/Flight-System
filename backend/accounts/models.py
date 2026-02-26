from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class UserRole(models.Model):
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    image = models.ImageField(upload_to="profiles/", null=True, blank=True)
    user_role = models.ForeignKey(
        "accounts.UserRole",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username


class AirlineCompany(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey("geo.Country", on_delete=models.CASCADE)
    website = models.URLField(max_length=200, null=True, blank=True)
    logo = models.TextField(null=True, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="airline_profile"
    )

    def get_logo_url(self, request=None):
        if not self.logo:
            return None

        logo_value = self.logo.strip()
        if not logo_value:
            return None

        if logo_value.startswith(("data:", "http://", "https://")):
            return logo_value

        media_url = settings.MEDIA_URL or "/media/"
        if logo_value.startswith("/"):
            logo_url = logo_value
        else:
            logo_url = f"{media_url.rstrip('/')}/{logo_value.lstrip('/')}"

        if request is not None:
            return request.build_absolute_uri(logo_url)
        return logo_url

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=15, unique=True)
    credit_card_no = models.CharField(max_length=13, unique=True)
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
