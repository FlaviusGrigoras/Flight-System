from django.urls import path

from .views import (
    FlightListAPIView,
    FlightDetailAPIView,
    ArrivalFlightsAPIView,
    DepartureFlightsAPIView,
    AirlineFlightsAPIView,
    AirlineFlightDetailAPIView,
)


urlpatterns = [
    path("", FlightListAPIView.as_view(), name="flight-list"),
    path("arrivals/", ArrivalFlightsAPIView.as_view(), name="flight-arrivals"),
    path("departures/", DepartureFlightsAPIView.as_view(), name="flight-departures"),
    path("<int:pk>/", FlightDetailAPIView.as_view(), name="flight-detail"),
    path("my-flights/", AirlineFlightsAPIView.as_view(), name="airline-flights"),
    path(
        "my-flights/<int:pk>/",
        AirlineFlightDetailAPIView.as_view(),
        name="airline-flight-detail",
    ),
]
