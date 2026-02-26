from datetime import timedelta

import pytest
from rest_framework.test import APIClient
from django.utils import timezone

from accounts.models import Administrator, AirlineCompany, Customer, User
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
        user=customer_user,
        first_name="Ticket",
        last_name="Buyer",
        address="1 Ticket Lane",
        phone_no="PH00000000002",
        credit_card_no="0000000000002",
    )

    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=cdg,
        departure_time=timezone.now() + timedelta(days=1),
        landing_time=timezone.now() + timedelta(days=1, hours=3),
        remaining_tickets=20,
        economy_seats=12,
        business_seats=8,
        remaining_economy_tickets=12,
        remaining_business_tickets=8,
        economy_price=100,
        business_price=180,
    )

    customer_client = APIClient()
    customer_client.force_authenticate(user=customer_user)
    purchase_response = customer_client.post(
        "/api/tickets/purchase/",
        {"flight_id": flight.id, "cabin_class": "ECONOMY"},
        format="json",
    )

    assert purchase_response.status_code == 201
    assert Ticket.objects.filter(flight=flight, customer=customer).exists()
    assert purchase_response.data["seat_no"] == "3A"

    flight.refresh_from_db()
    assert flight.remaining_tickets == 19

    airline_client = APIClient()
    airline_client.force_authenticate(user=airline_user)
    sold_response = airline_client.get(f"/api/tickets/airline/sold/?flight_id={flight.id}")

    assert sold_response.status_code == 200
    assert len(sold_response.data) == 1
    assert sold_response.data[0]["flight"]["id"] == flight.id


@pytest.mark.django_db
def test_ticket_purchase_allows_8_tickets_and_my_tickets_returns_all():
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
        username="duplicate-airline-owner",
        email="duplicate-airline-owner@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Duplicate Layered Air", country=country_ro, user=airline_user
    )

    customer_user = User.objects.create_user(
        username="duplicate-ticket-customer",
        email="duplicate-ticket-customer@example.com",
        password="StrongPass123",
    )
    Customer.objects.create(
        user=customer_user,
        first_name="Duplicate",
        last_name="Buyer",
        address="3 Duplicate Street",
        phone_no="PH00000000004",
        credit_card_no="0000000000004",
    )

    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=cdg,
        departure_time=timezone.now() + timedelta(days=1),
        landing_time=timezone.now() + timedelta(days=1, hours=3),
        remaining_tickets=20,
        economy_seats=12,
        business_seats=8,
        remaining_economy_tickets=12,
        remaining_business_tickets=8,
        economy_price=100,
        business_price=180,
    )

    client = APIClient()
    client.force_authenticate(user=customer_user)

    for _ in range(8):
        purchase = client.post(
            "/api/tickets/purchase/",
            {"flight_id": flight.id, "cabin_class": "ECONOMY"},
            format="json",
        )
        assert purchase.status_code == 201

    tickets = list(
        Ticket.objects.filter(flight=flight, customer__user=customer_user).order_by("id")
    )
    assert len(tickets) == 8
    assert [ticket.seat_no for ticket in tickets] == [
        "3A",
        "3B",
        "3C",
        "3D",
        "3E",
        "3F",
        "4A",
        "4B",
    ]

    my_tickets_response = client.get("/api/tickets/my-tickets/")
    assert my_tickets_response.status_code == 200
    assert len(my_tickets_response.data) == 8


@pytest.mark.django_db
def test_ticket_seat_assignment_places_business_rows_before_economy_rows():
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
        username="seat-order-airline-owner",
        email="seat-order-airline-owner@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Seat Order Airline", country=country_ro, user=airline_user
    )

    customer_user = User.objects.create_user(
        username="seat-order-ticket-customer",
        email="seat-order-ticket-customer@example.com",
        password="StrongPass123",
    )
    Customer.objects.create(
        user=customer_user,
        first_name="Seat",
        last_name="Order",
        address="4 Seat Street",
        phone_no="PH00000000005",
        credit_card_no="0000000000005",
    )

    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=cdg,
        departure_time=timezone.now() + timedelta(days=1),
        landing_time=timezone.now() + timedelta(days=1, hours=3),
        remaining_tickets=20,
        economy_seats=12,
        business_seats=8,
        remaining_economy_tickets=12,
        remaining_business_tickets=8,
        economy_price=100,
        business_price=180,
    )

    client = APIClient()
    client.force_authenticate(user=customer_user)

    business_purchase = client.post(
        "/api/tickets/purchase/",
        {"flight_id": flight.id, "cabin_class": "BUSINESS"},
        format="json",
    )
    economy_purchase = client.post(
        "/api/tickets/purchase/",
        {"flight_id": flight.id, "cabin_class": "ECONOMY"},
        format="json",
    )

    assert business_purchase.status_code == 201
    assert economy_purchase.status_code == 201
    assert business_purchase.data["seat_no"] == "1A"
    assert economy_purchase.data["seat_no"] == "3A"


@pytest.mark.django_db
def test_airline_sold_endpoint_rejects_non_airline_user():
    country = Country.objects.create(name="Spain", iso2="ES")
    user = User.objects.create_user(
        username="not-airline",
        email="not-airline@example.com",
        password="StrongPass123",
    )
    Customer.objects.create(
        user=user,
        first_name="Not",
        last_name="Airline",
        address="2 Example Street",
        phone_no="PH00000000003",
        credit_card_no="0000000000003",
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/tickets/airline/sold/")

    assert response.status_code == 403

    refund_response = client.post("/api/tickets/1/refund/")
    assert refund_response.status_code == 403


@pytest.mark.django_db
def test_airline_must_refund_tickets_before_deleting_flight():
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
        username="delete-after-refund-airline",
        email="delete-after-refund-airline@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Refund First Airline", country=country_ro, user=airline_user
    )

    customer_user = User.objects.create_user(
        username="delete-after-refund-customer",
        email="delete-after-refund-customer@example.com",
        password="StrongPass123",
    )
    Customer.objects.create(
        user=customer_user,
        first_name="Refund",
        last_name="Required",
        address="5 Refund Street",
        phone_no="PH00000000006",
        credit_card_no="0000000000006",
    )

    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=cdg,
        departure_time=timezone.now() + timedelta(days=1),
        landing_time=timezone.now() + timedelta(days=1, hours=3),
        remaining_tickets=20,
        economy_seats=12,
        business_seats=8,
        remaining_economy_tickets=12,
        remaining_business_tickets=8,
        economy_price=100,
        business_price=180,
    )

    customer_client = APIClient()
    customer_client.force_authenticate(user=customer_user)
    purchase_response = customer_client.post(
        "/api/tickets/purchase/",
        {"flight_id": flight.id, "cabin_class": "ECONOMY"},
        format="json",
    )
    assert purchase_response.status_code == 201
    ticket_id = purchase_response.data["id"]

    airline_client = APIClient()
    airline_client.force_authenticate(user=airline_user)

    delete_response = airline_client.delete(f"/api/flights/my-flights/{flight.id}/")
    assert delete_response.status_code == 400
    assert (
        "Refund all purchased tickets first"
        in delete_response.data["error"]["message"]
    )

    refund_response = airline_client.post(f"/api/tickets/{ticket_id}/refund/")
    assert refund_response.status_code == 200
    assert refund_response.data["status"] == Ticket.Status.REFUNDED

    my_tickets_response = customer_client.get("/api/tickets/my-tickets/")
    assert my_tickets_response.status_code == 200
    refunded = next(
        item for item in my_tickets_response.data if item["id"] == ticket_id
    )
    assert refunded["status"] == Ticket.Status.REFUNDED

    flight.refresh_from_db()
    assert flight.remaining_tickets == 20
    assert flight.remaining_economy_tickets == 12

    delete_after_refund = airline_client.delete(f"/api/flights/my-flights/{flight.id}/")
    assert delete_after_refund.status_code == 204


@pytest.mark.django_db
def test_admin_can_list_and_refund_tickets():
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

    admin_user = User.objects.create_user(
        username="ticket-admin",
        email="ticket-admin@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    Administrator.objects.create(
        user=admin_user,
        first_name="Ticket",
        last_name="Admin",
    )

    airline_user = User.objects.create_user(
        username="ticket-admin-airline",
        email="ticket-admin-airline@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Ticket Admin Airline", country=country_ro, user=airline_user
    )

    customer_user = User.objects.create_user(
        username="ticket-admin-customer",
        email="ticket-admin-customer@example.com",
        password="StrongPass123",
    )
    Customer.objects.create(
        user=customer_user,
        first_name="Ticket",
        last_name="Customer",
        address="6 Admin Street",
        phone_no="PH00000000007",
        credit_card_no="0000000000007",
    )

    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=cdg,
        departure_time=timezone.now() + timedelta(days=1),
        landing_time=timezone.now() + timedelta(days=1, hours=3),
        remaining_tickets=20,
        economy_seats=12,
        business_seats=8,
        remaining_economy_tickets=12,
        remaining_business_tickets=8,
        economy_price=100,
        business_price=180,
    )

    customer_client = APIClient()
    customer_client.force_authenticate(user=customer_user)
    purchase_response = customer_client.post(
        "/api/tickets/purchase/",
        {"flight_id": flight.id, "cabin_class": "BUSINESS"},
        format="json",
    )
    assert purchase_response.status_code == 201
    ticket_id = purchase_response.data["id"]

    admin_client = APIClient()
    admin_client.force_authenticate(user=admin_user)
    list_response = admin_client.get("/api/tickets/admin/all/")
    assert list_response.status_code == 200
    assert any(item["id"] == ticket_id for item in list_response.data)

    refund_response = admin_client.post(f"/api/tickets/{ticket_id}/refund/")
    assert refund_response.status_code == 200
    assert refund_response.data["status"] == Ticket.Status.REFUNDED

    ticket = Ticket.objects.get(id=ticket_id)
    assert ticket.status == Ticket.Status.REFUNDED
