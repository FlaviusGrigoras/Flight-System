from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Administrator, AirlineCompany, Customer, User
from core.exceptions import ForbiddenError, ValidationDomainError
from facades.administrator_facade import AdministratorFacade
from facades.airline_facade import AirlineFacade
from facades.anonymous_facade import AnonymousFacade
from facades.base_facade import FacadeBase
from facades.customer_facade import CustomerFacade
from flights.models import Flight
from geo.models import Airport, Country
from tickets.models import Ticket


def _create_route_fixture():
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
    return country_ro, country_it, otp, fco


@pytest.mark.django_db
def test_base_facade_covers_pdf_required_methods():
    facade = FacadeBase()
    country_ro, country_it, otp, fco = _create_route_fixture()

    admin_user = User.objects.create_user(
        username="base-admin",
        email="base-admin@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    admin = Administrator.objects.create(
        user=admin_user,
        first_name="Base",
        last_name="Admin",
    )

    airline_user = facade.create_user(
        username="base-airline",
        password="StrongPass123",
        email="base-airline@example.com",
    )
    airline = facade.add_airline(
        AirlineCompany(
            name="Base Airline",
            country=country_ro,
            user=airline_user,
        )
    )

    departure = timezone.now() + timedelta(hours=2)
    landing = departure + timedelta(hours=2)
    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=fco,
        departure_time=departure,
        landing_time=landing,
        remaining_tickets=12,
        economy_seats=6,
        business_seats=6,
        remaining_economy_tickets=6,
        remaining_business_tickets=6,
        economy_price=120,
        business_price=200,
    )

    customer_user = facade.create_user(
        username="base-customer",
        password="StrongPass123",
        email="base-customer@example.com",
    )
    customer = facade.add_customer(
        Customer(
            user=customer_user,
            first_name="Base",
            last_name="Customer",
            address="Base Address",
            phone_no="PH00000000011",
            credit_card_no="0000000000011",
        )
    )

    assert customer.id is not None
    assert customer.user.user_role.role_name == "Customer"
    assert airline.user.user_role.role_name == "Airline Company"

    all_flight_ids = {item.id for item in facade.get_all_flights()}
    assert flight.id in all_flight_ids
    assert facade.get_flight_by_id(flight.id).id == flight.id

    by_params_ids = {
        item.id
        for item in facade.get_flights_by_parameters(
            country_ro.id,
            country_it.id,
            departure.date(),
        )
    }
    assert flight.id in by_params_ids
    assert flight.id in {item.id for item in facade.get_departure_flights(country_ro.id)}
    assert flight.id in {item.id for item in facade.get_arrival_flights(country_it.id)}

    assert airline.id in {item.id for item in facade.get_all_airlines()}
    assert facade.get_airline_by_id(airline.id).id == airline.id
    assert country_ro.id in {item.id for item in facade.get_all_countries()}
    assert facade.get_country_by_id(country_it.id).id == country_it.id
    assert otp.id in {
        airport.id
        for airport in facade.search_airports(
            country_id=country_ro.id,
            query="Henri",
            limit=5,
        )
    }
    assert admin.id in {item.id for item in facade.get_all_administrators()}

    first_candidate = facade.generate_unique_username_from_email("duplicate@example.com")
    facade.create_user(
        username=first_candidate,
        password="StrongPass123",
        email="duplicate+1@example.com",
    )
    second_candidate = facade.generate_unique_username_from_email("duplicate@example.com")
    assert second_candidate != first_candidate


@pytest.mark.django_db
def test_anonymous_facade_supports_registration_and_login_with_roles():
    country_ro = Country.objects.create(name="Romania", iso2="RO")
    facade = AnonymousFacade()

    customer = facade.add_customer(
        user_data={
            "username": "anon-customer",
            "password": "StrongPass123",
            "email": "anon-customer@example.com",
        },
        customer_data={
            "first_name": "Anon",
            "last_name": "Customer",
            "address": "Anon Address",
            "phone_no": "PH00000000012",
            "credit_card_no": "0000000000012",
        },
    )
    airline = facade.add_airline(
        user_data={
            "username": "anon-airline",
            "password": "StrongPass123",
            "email": "anon-airline@example.com",
        },
        airline_data={
            "name": "Anon Wings",
            "country_id": country_ro.id,
        },
    )

    assert customer.user.user_role.role_name == "Customer"
    assert airline.user.user_role.role_name == "Airline Company"

    logged_in = facade.login("anon-customer@example.com", "StrongPass123")
    assert logged_in.id == customer.user_id

    User.objects.create_user(
        username="same-email-1",
        email="same-email@example.com",
        password="StrongPass123",
    )
    User.objects.create_user(
        username="same-email-2",
        email="same-email@example.com",
        password="StrongPass123",
    )
    with pytest.raises(ValidationDomainError):
        facade.login("same-email@example.com", "StrongPass123")


@pytest.mark.django_db
def test_customer_facade_purchase_cancel_get_and_profile_updates():
    country_ro, country_it, otp, fco = _create_route_fixture()

    airline_user = User.objects.create_user(
        username="customer-flow-airline",
        email="customer-flow-airline@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Customer Flow Airline",
        country=country_ro,
        user=airline_user,
    )

    customer_user = User.objects.create_user(
        username="customer-flow-user",
        email="customer-flow@example.com",
        password="StrongPass123",
    )
    customer = Customer.objects.create(
        user=customer_user,
        first_name="Before",
        last_name="Update",
        address="Old Address",
        phone_no="PH00000000013",
        credit_card_no="0000000000013",
    )

    flight = Flight.objects.create(
        airline_company=airline,
        origin_airport=otp,
        destination_airport=fco,
        departure_time=timezone.now() + timedelta(days=1, hours=1),
        landing_time=timezone.now() + timedelta(days=1, hours=3),
        remaining_tickets=10,
        economy_seats=6,
        business_seats=4,
        remaining_economy_tickets=6,
        remaining_business_tickets=4,
        economy_price=100,
        business_price=180,
    )

    facade = CustomerFacade(customer_user)

    ticket = facade.purchase_ticket(flight.id, cabin_class=Ticket.CabinClass.ECONOMY)
    assert ticket.id is not None
    assert ticket.customer_id == customer.id
    assert ticket.status == Ticket.Status.ACTIVE

    my_tickets = list(facade.get_my_tickets())
    assert len(my_tickets) == 1
    assert my_tickets[0].id == ticket.id

    second_ticket = facade.purchase_ticket(
        flight.id, cabin_class=Ticket.CabinClass.ECONOMY
    )
    assert second_ticket.id is not None
    assert second_ticket.id != ticket.id

    my_tickets = list(facade.get_my_tickets())
    assert len(my_tickets) == 2
    assert [t.seat_no for t in my_tickets] == ["2A", "2B"]

    cancelled = facade.cancel_ticket(ticket.id)
    assert cancelled.status == Ticket.Status.CANCELLED

    updated = facade.update_customer(
        {
            "first_name": "After",
            "last_name": "Update",
            "address": "New Address",
            "phone_no": "PH00000000014",
            "credit_card_no": "0000000000014",
            "email": "customer-flow-updated@example.com",
        }
    )
    updated.refresh_from_db()
    updated.user.refresh_from_db()
    assert updated.first_name == "After"
    assert updated.address == "New Address"
    assert updated.user.email == "customer-flow-updated@example.com"


@pytest.mark.django_db
def test_customer_facade_rejects_invalid_profile_updates():
    User.objects.create_user(
        username="plain-user",
        email="plain-user@example.com",
        password="StrongPass123",
    )

    user_a = User.objects.create_user(
        username="customer-a",
        email="customer-a@example.com",
        password="StrongPass123",
    )
    customer_a = Customer.objects.create(
        user=user_a,
        first_name="A",
        last_name="A",
        address="Addr A",
        phone_no="PH00000000015",
        credit_card_no="0000000000015",
    )

    user_b = User.objects.create_user(
        username="customer-b",
        email="customer-b@example.com",
        password="StrongPass123",
    )
    Customer.objects.create(
        user=user_b,
        first_name="B",
        last_name="B",
        address="Addr B",
        phone_no="PH00000000016",
        credit_card_no="0000000000016",
    )

    facade = CustomerFacade(user_a)
    with pytest.raises(ValidationDomainError):
        facade.update_customer({"phone_no": "PH00000000016"})

    with pytest.raises(ValidationDomainError):
        facade.update_customer({"email": "customer-b@example.com"})

    with pytest.raises(ValidationDomainError):
        facade.update_customer({"address": ""})

    normal_user = User.objects.get(username="plain-user")
    non_customer_facade = CustomerFacade(normal_user)
    with pytest.raises(ValidationDomainError):
        non_customer_facade.update_customer({"address": "Nope"})

    assert customer_a.id is not None


@pytest.mark.django_db
def test_airline_facade_valid_and_invalid_rules_from_pdf():
    country_ro, country_it, otp, fco = _create_route_fixture()

    airline_user = User.objects.create_user(
        username="airline-facade-user",
        email="airline-facade-user@example.com",
        password="StrongPass123",
    )
    AirlineCompany.objects.create(
        name="Airline Facade Airline",
        country=country_ro,
        user=airline_user,
    )

    facade = AirlineFacade(airline_user.username)
    departure = timezone.now() + timedelta(days=1, hours=2)
    landing = departure + timedelta(hours=2)

    valid_flight_data = {
        "origin_airport": otp,
        "destination_airport": fco,
        "departure_time": departure,
        "landing_time": landing,
        "economy_seats": 6,
        "business_seats": 4,
        "economy_price": 120,
        "business_price": 190,
    }

    created = facade.add_flight(valid_flight_data)
    assert created.id is not None
    assert created.remaining_tickets == 10

    my_flights = list(facade.get_my_flights())
    assert created.id in {item.id for item in my_flights}

    with pytest.raises(ValidationDomainError):
        facade.add_flight(
            {
                **valid_flight_data,
                "economy_seats": -6,
            }
        )

    with pytest.raises(ValidationDomainError):
        facade.add_flight(
            {
                **valid_flight_data,
                "landing_time": departure,
            }
        )

    with pytest.raises(ValidationDomainError):
        facade.add_flight(
            {
                **valid_flight_data,
                "departure_time": timezone.now() - timedelta(days=1),
                "landing_time": timezone.now() + timedelta(hours=1),
            }
        )

    with pytest.raises(ValidationDomainError):
        facade.update_flight(
            created.id,
            {"origin_airport": otp, "destination_airport": otp},
        )

    facade.remove_flight(created.id)
    assert Flight.objects.filter(id=created.id).exists() is False

    non_airline_user = User.objects.create_user(
        username="non-airline-facade-user",
        email="non-airline-facade-user@example.com",
        password="StrongPass123",
    )
    with pytest.raises(ForbiddenError):
        AirlineFacade(non_airline_user.username).get_my_flights()


@pytest.mark.django_db
def test_administrator_facade_add_airline_sets_role():
    admin_user = User.objects.create_user(
        username="admin-role-user",
        email="admin-role-user@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    Administrator.objects.create(
        user=admin_user,
        first_name="Role",
        last_name="Admin",
    )
    country = Country.objects.create(name="Spain", iso2="ES")

    facade = AdministratorFacade(admin_user)
    new_airline = facade.add_airline(
        user_data={
            "username": "role-airline",
            "password": "StrongPass123",
            "email": "role-airline@example.com",
        },
        airline_data={"name": "Role Airline", "country_id": country.id},
    )
    new_airline.user.refresh_from_db()
    assert new_airline.user.user_role.role_name == "Airline Company"


@pytest.mark.django_db
def test_customer_me_api_updates_profile():
    user = User.objects.create_user(
        username="api-customer-profile",
        email="api-customer-profile@example.com",
        password="StrongPass123",
    )
    customer = Customer.objects.create(
        user=user,
        first_name="Api",
        last_name="Customer",
        address="Old Address",
        phone_no="PH00000000017",
        credit_card_no="0000000000017",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/api/accounts/customer/me/",
        {
            "first_name": "Updated",
            "address": "Updated Address",
            "phone_no": "PH00000000018",
            "credit_card_no": "0000000000018",
            "email": "api-customer-profile-updated@example.com",
        },
        format="json",
    )

    assert response.status_code == 200, response.data
    customer.refresh_from_db()
    customer.user.refresh_from_db()
    assert customer.first_name == "Updated"
    assert customer.address == "Updated Address"
    assert customer.phone_no == "PH00000000018"
    assert customer.credit_card_no == "0000000000018"
    assert customer.user.email == "api-customer-profile-updated@example.com"
