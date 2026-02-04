from django.contrib import admin
from .models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "airline_company",
        "origin_airport",
        "destination_airport",
        "departure_time",
        "landing_time",
        "remaining_tickets",
    )
    list_filter = (
        "airline_company",
        "departure_time",
        "origin_airport__country",
        "destination_airport__country",
    )
    search_fields = (
        "origin_airport__iata_code",
        "destination_airport__iata_code",
        "origin_airport__name",
        "destination_airport__name",
    )

    autocomplete_fields = ("origin_airport", "destination_airport", "airline_company")
