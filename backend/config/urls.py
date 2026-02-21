from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.api.urls")),
    path("api/flights/", include("flights.api.urls")),
    path("api/geo/", include("geo.api.urls")),
    path("api/tickets/", include("tickets.api.urls")),
]
