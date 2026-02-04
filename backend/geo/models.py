from django.db import models


class Country(models.Model):
    iso2 = models.CharField(max_length=2, unique=True, null=True, blank=True)
    name = models.CharField(max_length=128, unique=True)
    flag_url = models.URLField(blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.iso2 or '--'})"


class Airport(models.Model):
    iata_code = models.CharField(max_length=3, blank=True, default="", db_index=True)
    icao_code = models.CharField(max_length=4, blank=True, default="", db_index=True)

    name = models.CharField(max_length=255)
    city = models.CharField(max_length=128, blank=True, default="")
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, related_name="airports"
    )

    class Meta:
        ordering = ["country__name", "city", "name"]

    def __str__(self) -> str:
        code = self.iata_code or self.icao_code or "N/A"
        city = self.city.strip()
        city_part = f"{city}, " if city else ""
        return f"{code} - {self.name} ({city_part}{self.country.iso2 or '--'})"
