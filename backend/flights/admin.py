from django.contrib import admin
from .models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "airline_company",
        "origin_country",
        "destination_country",
        "departure_time",
        "remaining_tickets",
    )

    list_filter = ("airline_company",)
    search_fields = ("airline_company__name",)
