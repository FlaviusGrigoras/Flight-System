from io import BytesIO
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from accounts.models import Administrator, AirlineCompany, Customer, User
from core.exceptions import ForbiddenError, ValidationDomainError
from facades.administrator_facade import AdministratorFacade
from flights.models import Flight
from geo.models import Airport, Country


@pytest.mark.django_db
def test_administrator_facade_can_manage_entities():
    admin_user = User.objects.create_user(
        username="root-admin",
        email="root@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    Administrator.objects.create(
        user=admin_user, first_name="Root", last_name="Administrator"
    )
    facade = AdministratorFacade(admin_user)

    country = Country.objects.create(name="Romania", iso2="RO")

    customer_user = User.objects.create_user(
        username="customer-user",
        email="customer@example.com",
        password="StrongPass123",
    )
    customer = Customer.objects.create(
        user=customer_user,
        first_name="Ada",
        last_name="Lovelace",
        address="42 Logic Street",
        phone_no="PH00000000001",
        credit_card_no="0000000000001",
    )

    airline_user = User.objects.create_user(
        username="airline-user",
        email="airline@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        user=airline_user, name="Sky One", country=country
    )

    new_admin = facade.add_administrator(
        user_data={
            "username": "new-admin",
            "password": "StrongPass123",
            "email": "newadmin@example.com",
        },
        admin_data={"first_name": "New", "last_name": "Admin"},
    )
    new_admin.user.refresh_from_db()
    assert new_admin.user.is_superuser is True
    assert new_admin.user.is_staff is True

    assert facade.remove_customer(customer.id) is True
    assert not Customer.objects.filter(id=customer.id).exists()
    assert not User.objects.filter(id=customer_user.id).exists()

    assert facade.remove_airline(airline.id) is True
    assert not AirlineCompany.objects.filter(id=airline.id).exists()
    assert not User.objects.filter(id=airline_user.id).exists()


@pytest.mark.django_db
def test_administrator_facade_rejects_non_admin_user():
    normal_user = User.objects.create_user(
        username="normal-user",
        email="normal@example.com",
        password="StrongPass123",
    )

    with pytest.raises(ForbiddenError):
        AdministratorFacade(normal_user)


@pytest.mark.django_db
def test_administrator_cannot_remove_self():
    admin_user = User.objects.create_user(
        username="self-admin",
        email="selfadmin@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    admin_profile = Administrator.objects.create(
        user=admin_user, first_name="Self", last_name="Admin"
    )
    facade = AdministratorFacade(admin_user)

    with pytest.raises(ValidationDomainError):
        facade.remove_administrator(admin_profile.id)


@pytest.mark.django_db
def test_admin_api_create_and_list_administrators():
    admin_user = User.objects.create_user(
        username="api-admin",
        email="apiadmin@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    Administrator.objects.create(user=admin_user, first_name="API", last_name="Admin")

    client = APIClient()
    client.force_authenticate(user=admin_user)

    create_response = client.post(
        "/api/accounts/admin/administrators/",
        {
            "email": "created-admin@example.com",
            "password": "StrongPass123",
            "first_name": "Created",
            "last_name": "Admin",
        },
        format="json",
    )
    assert create_response.status_code == 201
    created_admin_id = create_response.data["id"]

    created_admin = Administrator.objects.get(id=created_admin_id)
    assert created_admin.user.is_superuser is True
    assert created_admin.user.is_staff is True

    list_response = client.get("/api/accounts/admin/administrators/")
    assert list_response.status_code == 200
    returned_ids = {item["id"] for item in list_response.data}
    assert created_admin_id in returned_ids


@pytest.mark.django_db
def test_admin_api_create_airline():
    admin_user = User.objects.create_user(
        username="airline-admin",
        email="airlineadmin@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    Administrator.objects.create(
        user=admin_user, first_name="Airline", last_name="Admin"
    )
    country = Country.objects.create(name="Spain", iso2="ES")

    client = APIClient()
    client.force_authenticate(user=admin_user)

    create_response = client.post(
        "/api/accounts/admin/airlines/",
        {
            "username": "iberia-admin",
            "email": "iberia@example.com",
            "password": "StrongPass123",
            "name": "Iberia Test",
            "country_id": country.id,
        },
        format="json",
    )
    assert create_response.status_code == 201
    created_airline_id = create_response.data["id"]

    created_airline = AirlineCompany.objects.get(id=created_airline_id)
    assert created_airline.user.username == "iberia-admin"
    assert created_airline.user.email == "iberia@example.com"

    list_response = client.get("/api/accounts/admin/airlines/")
    assert list_response.status_code == 200
    returned_ids = {item["id"] for item in list_response.data}
    assert created_airline_id in returned_ids


@pytest.mark.django_db
def test_admin_api_delete_airline_with_flights_returns_validation_error():
    admin_user = User.objects.create_user(
        username="delete-airline-admin",
        email="delete-airline-admin@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    Administrator.objects.create(
        user=admin_user, first_name="Delete", last_name="Admin"
    )
    country = Country.objects.create(name="Germany", iso2="DE")
    origin_airport = Airport.objects.create(
        iata_code="FRA",
        icao_code="EDDF",
        name="Frankfurt Airport",
        city="Frankfurt",
        country=country,
    )
    destination_airport = Airport.objects.create(
        iata_code="MUC",
        icao_code="EDDM",
        name="Munich Airport",
        city="Munich",
        country=country,
    )
    airline_user = User.objects.create_user(
        username="delete-airline-user",
        email="delete-airline-user@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        user=airline_user, name="Delete Airline", country=country
    )
    now = timezone.now()
    Flight.objects.create(
        airline_company=airline,
        origin_airport=origin_airport,
        destination_airport=destination_airport,
        departure_time=now + timedelta(days=1),
        landing_time=now + timedelta(days=1, hours=2),
        remaining_tickets=10,
        economy_seats=6,
        business_seats=4,
        remaining_economy_tickets=6,
        remaining_business_tickets=4,
        economy_price=100,
        business_price=180,
    )

    client = APIClient()
    client.force_authenticate(user=admin_user)

    response = client.delete(f"/api/accounts/admin/airlines/{airline.id}/")

    assert response.status_code == 400
    assert response.data["error"]["code"] == "VALIDATION_ERROR"
    assert "Cannot remove airline" in response.data["error"]["message"]
    assert AirlineCompany.objects.filter(id=airline.id).exists()
    assert User.objects.filter(id=airline_user.id).exists()


@pytest.mark.django_db
def test_admin_api_requires_superuser():
    normal_user = User.objects.create_user(
        username="regular-user",
        email="regular@example.com",
        password="StrongPass123",
    )
    country = Country.objects.create(name="Portugal", iso2="PT")
    client = APIClient()
    client.force_authenticate(user=normal_user)

    response = client.get("/api/accounts/admin/customers/")
    assert response.status_code == 403

    create_airline_response = client.post(
        "/api/accounts/admin/airlines/",
        {
            "username": "restricted-airline",
            "email": "restricted@example.com",
            "password": "StrongPass123",
            "name": "Restricted Airline",
            "country_id": country.id,
        },
        format="json",
    )
    assert create_airline_response.status_code == 403


@pytest.mark.django_db
def test_current_user_endpoint_marks_superuser_as_administrator():
    superuser = User.objects.create_user(
        username="root-user",
        email="rootuser@example.com",
        password="StrongPass123",
        is_superuser=True,
        is_staff=True,
    )
    client = APIClient()
    client.force_authenticate(user=superuser)

    response = client.get("/api/accounts/me/")
    assert response.status_code == 200
    assert response.data["role"] == "administrator"


@pytest.mark.django_db
def test_airline_logo_upload_is_stored_in_database_and_returned_as_data_url():
    country = Country.objects.create(name="France", iso2="FR")
    airline_user = User.objects.create_user(
        username="logo-airline",
        email="logo-airline@example.com",
        password="StrongPass123",
    )
    airline = AirlineCompany.objects.create(
        name="Logo DB Air",
        country=country,
        user=airline_user,
    )

    client = APIClient()
    client.force_authenticate(user=airline_user)

    image_buffer = BytesIO()
    Image.new("RGB", (1, 1), color="white").save(image_buffer, format="PNG")
    logo_file = SimpleUploadedFile(
        "logo.png",
        image_buffer.getvalue(),
        content_type="image/png",
    )

    update_response = client.patch(
        "/api/accounts/airline/me/",
        {"logo": logo_file},
        format="multipart",
    )
    assert update_response.status_code == 200, update_response.data
    assert update_response.data["logo_url"].startswith("data:image/png;base64,")

    airline.refresh_from_db()
    assert airline.logo.startswith("data:image/png;base64,")
    assert airline.logo == update_response.data["logo_url"]

    me_response = client.get("/api/accounts/me/")
    assert me_response.status_code == 200
    assert me_response.data["airline_company"]["logo_url"] == airline.logo
