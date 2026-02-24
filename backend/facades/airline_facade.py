from facades.base_facade import FacadeBase
from core.exceptions import ForbiddenError, ValidationDomainError, NotFoundError
from django.utils import timezone
from flights.models import Flight
from tickets.repositories.ticket_repository import TicketRepository
import logging

logger = logging.getLogger("flights")


class AirlineFacade(FacadeBase):
    def __init__(self, user_id):
        super().__init__()
        self.airline_company = self.airline_repo.get_airline_by_username(user_id)
        self.ticket_repo = TicketRepository()

    def _validate_airline_ownership(self, fligt):
        if fligt.airline_company_id != self.airline_company.id:
            raise ForbiddenError("You can only manage your own flights")

    def add_flight(self, flight_data):
        # flight_data -> origin_airport, destination_airport, departure_time, landing_time, remaining_tickets

        if not self.airline_company:
            raise ForbiddenError("User in not an airline company")

        def _to_pk(value, field_name: str) -> int:
            if isinstance(value, int):
                return value
            if value is None:
                raise ValidationDomainError(f"{field_name} is required")
            pk = getattr(value, "pk", None)
            if isinstance(pk, int):
                return pk
            raise ValidationDomainError(f"Invalid {field_name}")

        origin_airport_id = _to_pk(flight_data.get("origin_airport"), "origin_airport")
        destination_airport_id = _to_pk(
            flight_data.get("destination_airport"), "destination_airport"
        )

        if flight_data["remaining_tickets"] < 0:
            raise ValidationDomainError("Ticket count cannot be negative")

        if flight_data["landing_time"] <= flight_data["departure_time"]:
            raise ValidationDomainError("Landing time must be after departure time.")

        if flight_data["departure_time"] < timezone.now():
            raise ValidationDomainError("Cannot create flights in the past.")

        departure_local_date = timezone.localtime(flight_data["departure_time"]).date()
        if departure_local_date == timezone.localdate():
            raise ValidationDomainError(
                "Cannot create flights departing today. Choose a later date."
            )

        if origin_airport_id == destination_airport_id:
            raise ValidationDomainError("Origin and Destination cannot be the same.")

        new_flight = Flight(
            airline_company_id=self.airline_company.id,
            origin_airport_id=origin_airport_id,
            destination_airport_id=destination_airport_id,
            departure_time=flight_data["departure_time"],
            landing_time=flight_data["landing_time"],
            remaining_tickets=flight_data["remaining_tickets"],
        )
        self.flight_repo.add(new_flight)

        logger.info(
            f"Airline '{self.airline_company.name}' added a new flight from airport ID {origin_airport_id} to {destination_airport_id}."
        )
        return new_flight

    def update_flight(self, flight_id, update_data):
        flight = self.flight_repo.get_by_id(flight_id)
        if not flight:
            raise NotFoundError("Flight not found")

        self._validate_airline_ownership(flight)

        if flight.departure_time <= timezone.now():
            raise ValidationDomainError("Cannot modify a flight that already departed.")

        def _to_pk(value, field_name: str) -> int:
            if isinstance(value, int):
                return value
            if value is None:
                raise ValidationDomainError(f"{field_name} is required")
            pk = getattr(value, "pk", None)
            if isinstance(pk, int):
                return pk
            raise ValidationDomainError(f"Invalid {field_name}")

        if "airline_company" in update_data or "airline_company_id" in update_data:
            raise ValidationDomainError("airline_company cannot be changed.")

        if "origin_airport" in update_data:
            update_data["origin_airport_id"] = _to_pk(
                update_data.pop("origin_airport"), "origin_airport"
            )

        if "destination_airport" in update_data:
            update_data["destination_airport_id"] = _to_pk(
                update_data.pop("destination_airport"), "destination_airport"
            )

        if "remaining_tickets" in update_data and update_data["remaining_tickets"] < 0:
            raise ValidationDomainError("Ticket count cannot be negative")

        new_departure = update_data.get("departure_time", flight.departure_time)
        new_landing = update_data.get("landing_time", flight.landing_time)
        if new_landing <= new_departure:
            raise ValidationDomainError("Landing time must be after departure time.")
        if new_departure < timezone.now():
            raise ValidationDomainError("Cannot set departure time in the past.")
        if timezone.localtime(new_departure).date() == timezone.localdate():
            raise ValidationDomainError(
                "Cannot set departure time to today. Choose a later date."
            )

        new_origin_id = update_data.get("origin_airport_id", flight.origin_airport_id)
        new_destination_id = update_data.get(
            "destination_airport_id", flight.destination_airport_id
        )
        if new_origin_id == new_destination_id:
            raise ValidationDomainError("Origin and Destination cannot be the same.")

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

        if flight.departure_time <= timezone.now():
            raise ValidationDomainError("Cannot delete a flight that already departed.")

        logger.info(
            f"Airline '{self.airline_company.name}' removed flight ID {flight_id}."
        )

        return self.flight_repo.delete(flight_id)

    def get_my_flights(self):
        if not self.airline_company:
            raise ForbiddenError("Not an airline")
        return self.flight_repo.get_flights_by_airline_id(self.airline_company.id)

    def get_sold_tickets(self, flight_id=None):
        if not self.airline_company:
            raise ForbiddenError("User is not an airline company")
        return self.ticket_repo.get_tickets_by_airline(
            airline_company_id=self.airline_company.id, flight_id=flight_id
        )
