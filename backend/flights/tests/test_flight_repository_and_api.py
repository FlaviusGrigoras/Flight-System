from datetime import timedelta

import pytest
from rest_framework.test import APIClient
from django.utils import timezone

from accounts.models import AirlineCompany, User
from flights.models import Flight
from flights.repositories.flight_repository import FlightRepository
from geo.models import Airport, Country


@pytest.mark.django_db
def test_flight_repository_arrival_departure_queries():
    country_ro = Country.objects.create(name="Romania", iso2="RO")
    country_de = Country.objects.create(name="Germany", iso2="DE")

    otp = Airport.objects.create(
        name="Henri Coanda",
        city="Bucharest",
        iata_code="OTP",
        icao_code="LROP",
        country=country_ro,
    )
    clj = Airport.objects.create(
        name="Cluj Airport",
        city="Cluj",
        iata_code="CLJ",
        icao_code="LRCL",
        country=country_ro,
    )
    fra = Airport.objects.create(
        name="Frankfurt",
        city="Frankfurt",
        iata_code="FRA",
        icao_code="EDDF",
        country=country_de,
    )

    airline_user = User.objects.create_user(
        username="repo-airline",
        email="repo-airline@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Repository Air", country=country_ro, user=airline_user
    )

    now = timezone.now()
    arrival_match = Flight.objects.create(
        airline_company=airline,
        origin_airport=fra,
        destination_airport=otp,
        departure_time=now + timedelta(hours=1),
        landing_time=now + timedelta(hours=2),
        remaining_tickets=50,
    )
    departure_match = Flight.objects.create(
        airline_company=airline,
        origin_airport=clj,
        destination_airport=fra,
        departure_time=now + timedelta(hours=3),
        landing_time=now + timedelta(hours=5),
        remaining_tickets=50,
    )
    Flight.objects.create(
        airline_company=airline,
        origin_airport=fra,
        destination_airport=otp,
        departure_time=now + timedelta(hours=13),
        landing_time=now + timedelta(hours=14),
        remaining_tickets=50,
    )
    Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=fra,
        departure_time=now + timedelta(hours=13),
        landing_time=now + timedelta(hours=15),
        remaining_tickets=50,
    )

    repo = FlightRepository()
    arrival_ids = {flight.id for flight in repo.get_arrival_flights(country_ro.id)}
    departure_ids = {flight.id for flight in repo.get_departure_flights(country_ro.id)}

    assert arrival_match.id in arrival_ids
    assert departure_match.id not in arrival_ids

    assert departure_match.id in departure_ids
    assert arrival_match.id not in departure_ids


@pytest.mark.django_db
def test_flights_arrivals_and_departures_api():
    country_ro = Country.objects.create(name="Romania", iso2="RO")
    country_it = Country.objects.create(name="Italy", iso2="IT")

    otp = Airport.objects.create(
        name="Henri Coanda",
        city="Bucharest",
        iata_code="OTP",
        icao_code="LROP",
        country=country_ro,
    )
    fco = Airport.objects.create(
        name="Fiumicino",
        city="Rome",
        iata_code="FCO",
        icao_code="LIRF",
        country=country_it,
    )

    airline_user = User.objects.create_user(
        username="api-airline",
        email="api-airline@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="API Wings", country=country_ro, user=airline_user
    )

    now = timezone.now()
    arriving_flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=fco,
        destination_airport=otp,
        departure_time=now + timedelta(hours=2),
        landing_time=now + timedelta(hours=4),
        remaining_tickets=10,
    )
    departing_flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=fco,
        departure_time=now + timedelta(hours=1),
        landing_time=now + timedelta(hours=3),
        remaining_tickets=10,
    )

    client = APIClient()
    arrivals_response = client.get(f"/api/flights/arrivals/?country_id={country_ro.id}")
    departures_response = client.get(
        f"/api/flights/departures/?country_id={country_ro.id}"
    )

    assert arrivals_response.status_code == 200
    assert departures_response.status_code == 200

    arrivals_ids = {item["id"] for item in arrivals_response.data}
    departures_ids = {item["id"] for item in departures_response.data}

    assert arriving_flight.id in arrivals_ids
    assert departing_flight.id in departures_ids
