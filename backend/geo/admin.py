from django.contrib import admin
from .models import Country, Airport


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name", "iso2")
    search_fields = ("name", "iso2")


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    search_fields = (
        "iata_code",
        "icao_code",
        "name",
        "city",
        "country__name",
        "country__iso2",
    )
    list_display = ("iata_code", "icao_code", "name", "city", "country")
    list_filter = ("country",)
    ordering = ("country__name", "city", "name")
