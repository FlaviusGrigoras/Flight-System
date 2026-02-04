from django.contrib import admin
from .models import (
    User,
    AirlineCompany,
    Customer,
    Administrator,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")


@admin.register(AirlineCompany)
class AirlineCompanyAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "user")
    search_fields = ("first_name", "last_name", "phone_no")


admin.site.register(Administrator)
