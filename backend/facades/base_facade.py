from flights.repositories.flight_repository import FlightRepository
from accounts.repositories.airline_repository import AirlineCompanyRepository
from accounts.repositories.customer_repositories import CustomerRepository
from accounts.repositories.user_repository import UserRepository
from geo.repositories.country_repository import CountryRepository
from accounts.models import User


class FacadeBase:
    def __init__(self):
        self.flight_repo = FlightRepository()
        self.airline_repo = AirlineCompanyRepository()
        self.customer_repo = CustomerRepository()
        self.user_repo = UserRepository()
        self.country_repo = CountryRepository()

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

    def get_all_airlines(self):
        return self.airline_repo.get_all()

    def get_airline_by_id(self, airline_id):
        return self.airline_repo.get_by_id(airline_id)

    def get_all_countries(self):
        return self.country_repo.get_all()

    def get_country_by_id(self, country_id):
        return self.country_repo.get_by_id(country_id)

    def create_user(self, username, password, email):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        return user
