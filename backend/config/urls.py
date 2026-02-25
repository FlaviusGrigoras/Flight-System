from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.api.urls")),
    path("api/flights/", include("flights.api.urls")),
    path("api/geo/", include("geo.api.urls")),
    path("api/tickets/", include("tickets.api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
