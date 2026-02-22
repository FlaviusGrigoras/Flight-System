from django.urls import path
from geo.api.views import CountryListAPIView, AirportListAPIView

urlpatterns = [
    path("countries/", CountryListAPIView.as_view(), name="api-countries"),
    path("airports/", AirportListAPIView.as_view(), name="api-airports"),
]
