from django.contrib import admin
from .models import (
    User,
    UserRole,
    Country,
    AirlineCompany,
    Customer,
    Administrator,
    Flight,
    Ticket,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(AirlineCompany)
class AirlineCompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "airline_company",
        "origin_country",
        "destination_country",
        "departure_time",
        "remaining_tickets",
    )
    list_filter = ("origin_country", "destination_country", "airline_company")
    search_fields = ("airline_company__name",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "user")
    search_fields = ("first_name", "last_name", "phone_no")


admin.site.register(UserRole)
admin.site.register(Administrator)
admin.site.register(Ticket)
