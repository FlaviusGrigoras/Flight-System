from datetime import timedelta

import pytest
from rest_framework.test import APIClient
from django.utils import timezone

from accounts.models import AirlineCompany, Customer, User
from flights.models import Flight
from geo.models import Airport, Country
from tickets.models import Ticket


@pytest.mark.django_db
def test_ticket_purchase_and_airline_sold_api_flow():
    country_ro = Country.objects.create(name="Romania", iso2="RO")
    country_fr = Country.objects.create(name="France", iso2="FR")
    otp = Airport.objects.create(
        name="Henri Coanda",
        city="Bucharest",
        iata_code="OTP",
        icao_code="LROP",
        country=country_ro,
    )
    cdg = Airport.objects.create(
        name="Charles de Gaulle",
        city="Paris",
        iata_code="CDG",
        icao_code="LFPG",
        country=country_fr,
    )

    airline_user = User.objects.create_user(
        username="airline-owner",
        email="airline-owner@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Layered Air", country=country_ro, user=airline_user
    )

    customer_user = User.objects.create_user(
        username="ticket-customer",
        email="ticket-customer@example.com",
        password="StrongPass123",
    )
    customer = Customer.objects.create(
        user=customer_user, first_name="Ticket", last_name="Buyer"
    )

    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=cdg,
        departure_time=timezone.now() + timedelta(days=1),
        landing_time=timezone.now() + timedelta(days=1, hours=3),
        remaining_tickets=5,
    )

    customer_client = APIClient()
    customer_client.force_authenticate(user=customer_user)
    purchase_response = customer_client.post(
        "/api/tickets/purchase/",
        {"flight_id": flight.id},
        format="json",
    )

    assert purchase_response.status_code == 201
    assert Ticket.objects.filter(flight=flight, customer=customer).exists()

    flight.refresh_from_db()
    assert flight.remaining_tickets == 4

    airline_client = APIClient()
    airline_client.force_authenticate(user=airline_user)
    sold_response = airline_client.get(f"/api/tickets/airline/sold/?flight_id={flight.id}")

    assert sold_response.status_code == 200
    assert len(sold_response.data) == 1
    assert sold_response.data[0]["flight"]["id"] == flight.id


@pytest.mark.django_db
def test_airline_sold_endpoint_rejects_non_airline_user():
    country = Country.objects.create(name="Spain", iso2="ES")
    user = User.objects.create_user(
        username="not-airline",
        email="not-airline@example.com",
        password="StrongPass123",
    )
    Customer.objects.create(user=user, first_name="Not", last_name="Airline")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/tickets/airline/sold/")

    assert response.status_code == 403
