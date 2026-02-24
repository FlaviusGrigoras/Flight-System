import pytest
from rest_framework.test import APIClient

from accounts.models import Administrator, AirlineCompany, Customer, User
from core.exceptions import ForbiddenError, ValidationDomainError
from facades.administrator_facade import AdministratorFacade
from geo.models import Country


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
        user=customer_user, first_name="Ada", last_name="Lovelace"
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
    Administrator.objects.create(
        user=admin_user, first_name="API", last_name="Admin"
    )

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
def test_admin_api_requires_superuser():
    normal_user = User.objects.create_user(
        username="regular-user",
        email="regular@example.com",
        password="StrongPass123",
    )
    client = APIClient()
    client.force_authenticate(user=normal_user)

    response = client.get("/api/accounts/admin/customers/")
    assert response.status_code == 403
