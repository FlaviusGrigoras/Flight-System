from flights.repositories.flight_repository import FlightRepository
from accounts.repositories.airline_repository import AirlineCompanyRepository
from accounts.repositories.customer_repositories import CustomerRepository
from accounts.repositories.administrator_repository import AdministratorRepository
from accounts.repositories.user_repository import UserRepository
from geo.repositories.country_repository import CountryRepository
from geo.repositories.airport_repository import AirportRepository
from accounts.models import User, UserRole
import uuid


class FacadeBase:
    def __init__(self):
        self.flight_repo = FlightRepository()
        self.airline_repo = AirlineCompanyRepository()
        self.customer_repo = CustomerRepository()
        self.admin_repo = AdministratorRepository()
        self.user_repo = UserRepository()
        self.country_repo = CountryRepository()
        self.airport_repo = AirportRepository()

    def get_all_flights(self):
        return self.flight_repo.get_all()

    def get_flight_by_id(self, flight_id):
        return self.flight_repo.get_by_id(flight_id)

    def get_flights_by_parameters(
        self, origin_country_id, destination_country_id, date
    ):
        return self.flight_repo.get_flights_by_parameters(
            origin_country_id, destination_country_id, date
        )

    def get_arrival_flights(self, country_id):
        return self.flight_repo.get_arrival_flights(country_id)

    def get_departure_flights(self, country_id):
        return self.flight_repo.get_departure_flights(country_id)

    def get_all_airlines(self):
        return self.airline_repo.get_all()

    def get_airline_by_id(self, airline_id):
        return self.airline_repo.get_by_id(airline_id)

    def add_customer(self, customer):
        if (
            getattr(customer, "user_id", None)
            and getattr(customer.user, "user_role_id", None) is None
        ):
            customer.user.user_role = self._get_or_create_user_role("Customer")
            customer.user.save(update_fields=["user_role"])
        return self.customer_repo.add(customer)

    def add_airline(self, airline):
        if (
            getattr(airline, "user_id", None)
            and getattr(airline.user, "user_role_id", None) is None
        ):
            airline.user.user_role = self._get_or_create_user_role("Airline Company")
            airline.user.save(update_fields=["user_role"])
        return self.airline_repo.add(airline)

    def get_all_countries(self):
        return self.country_repo.get_all()

    def get_country_by_id(self, country_id):
        return self.country_repo.get_by_id(country_id)

    def search_airports(self, country_id=None, country_iso2=None, query=None, limit=None):
        return self.airport_repo.search(
            country_id=country_id,
            country_iso2=country_iso2,
            query=query,
            limit=limit,
        )

    def get_all_administrators(self):
        return self.admin_repo.get_all_with_users()

    def _get_or_create_user_role(self, role_name):
        role, _ = UserRole.objects.get_or_create(role_name=role_name)
        return role

    def create_user(self, username, password, email, user_role_name=None):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        if user_role_name:
            user.user_role = self._get_or_create_user_role(user_role_name)
            user.save(update_fields=["user_role"])
        return user

    def generate_unique_username_from_email(self, email):
        base = (email or "").strip().lower()[:150]

        if not self.user_repo.exists_by_username(base):
            return base

        while True:
            suffix = "-" + uuid.uuid4().hex[:8]
            candidate = base[: 150 - len(suffix)] + suffix
            if not self.user_repo.exists_by_username(candidate):
                return candidate
