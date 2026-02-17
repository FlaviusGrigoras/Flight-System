from facades.base_facade import FacadeBase
from core.exceptions import ForbiddenError, ValidationDomainError, NotFoundError
from django.utils import timezone
from flights.models import Flight
import logging

logger = logging.getLogger("flights")


class AirlineFacade(FacadeBase):
    def __init__(self, user_id):
        super().__init__()
        self.airline_company = self.airline_repo.get_airline_by_username(user_id)

    def _validate_airline_ownership(self, fligt):
        if fligt.airline_company_id != self.airline_company.id:
            raise ForbiddenError("You can only manage your own flights")

    def add_flight(self, flight_data):
        # flight_data -> origin_airport, destination_airport, departure_time, landing_time, remaining_tickets

        if not self.airline_company:
            raise ForbiddenError("User in not an airline company")

        if flight_data["remaining_tickets"] < 0:
            raise ValidationDomainError("Ticket count cannot be negative")

        if flight_data["landing_time"] <= flight_data["departure_time"]:
            raise ValidationDomainError("Landing time must be after departure time.")

        if flight_data["departure_time"] < timezone.now():
            raise ValidationDomainError("Cannot create flights in the past.")

        if flight_data["origin_airport"] == flight_data["destination_airport"]:
            raise ValidationDomainError("Origin and Destination cannot be the same.")

        new_flight = Flight(
            airline_company_id=self.airline_company.id,
            origin_airport_id=flight_data["origin_airport"],
            destination_airport_id=flight_data["destination_airport"],
            departure_time=flight_data["departure_time"],
            landing_time=flight_data["landing_time"],
            remaining_tickets=flight_data["remaining_tickets"],
        )
        self.flight_repo.add(new_flight)

        logger.info(
            f"Airline '{self.airline_company.name}' added a new flight from airport ID {flight_data['origin_airport']} to {flight_data['destination_airport']}."
        )
        return new_flight

    def update_flight(self, flight_id, update_data):
        flight = self.flight_repo.get_by_id(flight_id)
        if not flight:
            raise NotFoundError("Flight not found")

        self._validate_airline_ownership(flight)

        if "remaining_tickets" in update_data and update_data["remaining_tickets"] < 0:
            raise ValidationDomainError("Ticket count cannot be negative")

        for key, value in update_data.items():
            setattr(flight, key, value)

        logger.info(
            f"Airline '{self.airline_company.name}' updated flight ID {flight_id}."
        )

        return self.flight_repo.update(flight)

    def remove_flight(self, flight_id):
        flight = self.flight_repo.get_by_id(flight_id)
        if not flight:
            raise ValidationDomainError("Flight does not exist")

        self._validate_airline_ownership(flight)

        logger.info(
            f"Airline '{self.airline_company.name}' removed flight ID {flight_id}."
        )

        return self.flight_repo.delete(flight_id)

    def get_my_flights(self):
        if not self.airline_company:
            raise ForbiddenError("Not an airline")
        return self.flight_repo.get_flights_by_airline_id(self.airline_company.id)
