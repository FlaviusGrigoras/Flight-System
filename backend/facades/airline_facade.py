from facades.base_facade import FacadeBase
from core.exceptions import ForbiddenError, ValidationDomainError, NotFoundError
from django.utils import timezone
from django.db import transaction
from flights.models import Flight
from tickets.models import Ticket
from tickets.repositories.ticket_repository import TicketRepository
from decimal import Decimal, InvalidOperation
from datetime import timedelta, date
import calendar
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
        # flight_data -> origin_airport, destination_airport, departure_time, landing_time,
        # economy_seats, business_seats, economy_price, business_price, recurrence_frequency, recurrence_end_date

        if not self.airline_company:
            raise ForbiddenError("User in not an airline company")

        def _to_int(value, field_name: str) -> int:
            if value is None:
                raise ValidationDomainError(f"{field_name} is required")
            try:
                return int(value)
            except (TypeError, ValueError):
                raise ValidationDomainError(f"{field_name} must be an integer")

        def _to_price(value, field_name: str) -> Decimal:
            if value is None:
                raise ValidationDomainError(f"{field_name} is required")
            try:
                price = Decimal(str(value))
            except (TypeError, ValueError, InvalidOperation):
                raise ValidationDomainError(f"{field_name} must be a number")
            if price <= 0:
                raise ValidationDomainError(f"{field_name} must be greater than 0")
            return price

        def _add_months(day: date, months: int) -> date:
            year = day.year + (day.month - 1 + months) // 12
            month = (day.month - 1 + months) % 12 + 1
            last_day = calendar.monthrange(year, month)[1]
            return date(year, month, min(day.day, last_day))

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

        economy_seats = _to_int(flight_data.get("economy_seats"), "economy_seats")
        business_seats = _to_int(
            flight_data.get("business_seats"), "business_seats"
        )
        economy_price = _to_price(flight_data.get("economy_price"), "economy_price")
        business_price = _to_price(flight_data.get("business_price"), "business_price")

        if economy_seats <= 0 or economy_seats % 6 != 0:
            raise ValidationDomainError(
                "Economy seats must be a positive multiple of 6"
            )
        if business_seats <= 0 or business_seats % 4 != 0:
            raise ValidationDomainError(
                "Business seats must be a positive multiple of 4"
            )
        if economy_price == business_price:
            raise ValidationDomainError(
                "Economy and business prices must be different"
            )

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

        recurrence_frequency = flight_data.get("recurrence_frequency")
        recurrence_end_date = flight_data.get("recurrence_end_date")
        if recurrence_frequency:
            if recurrence_end_date is None:
                raise ValidationDomainError("recurrence_end_date is required")
            if isinstance(recurrence_end_date, str):
                try:
                    recurrence_end_date = date.fromisoformat(recurrence_end_date)
                except ValueError:
                    raise ValidationDomainError("recurrence_end_date is invalid")

            if recurrence_frequency not in {"daily", "every_2_days", "weekly", "monthly"}:
                raise ValidationDomainError("recurrence_frequency is invalid")

            max_end_date = _add_months(
                timezone.localtime(flight_data["departure_time"]).date(), 3
            )
            if recurrence_end_date > max_end_date:
                raise ValidationDomainError(
                    "recurrence_end_date cannot be more than 3 months after departure"
                )
            if recurrence_end_date < timezone.localtime(
                flight_data["departure_time"]
            ).date():
                raise ValidationDomainError(
                    "recurrence_end_date cannot be before departure date"
                )

        total_seats = economy_seats + business_seats
        duration = flight_data["landing_time"] - flight_data["departure_time"]

        def _build_flight(departure_time, landing_time):
            return Flight(
                airline_company_id=self.airline_company.id,
                origin_airport_id=origin_airport_id,
                destination_airport_id=destination_airport_id,
                departure_time=departure_time,
                landing_time=landing_time,
                remaining_tickets=total_seats,
                economy_seats=economy_seats,
                business_seats=business_seats,
                remaining_economy_tickets=economy_seats,
                remaining_business_tickets=business_seats,
                economy_price=economy_price,
                business_price=business_price,
            )

        created_flights = []
        current_departure = flight_data["departure_time"]
        current_landing = flight_data["landing_time"]

        with transaction.atomic():
            while True:
                if recurrence_end_date and timezone.localtime(current_departure).date() > recurrence_end_date:
                    break
                new_flight = _build_flight(current_departure, current_landing)
                self.flight_repo.add(new_flight)
                created_flights.append(new_flight)

                if not recurrence_frequency:
                    break

                if recurrence_frequency == "monthly":
                    next_departure_date = _add_months(
                        timezone.localtime(current_departure).date(), 1
                    )
                    current_departure = current_departure.replace(
                        year=next_departure_date.year,
                        month=next_departure_date.month,
                        day=next_departure_date.day,
                    )
                else:
                    days = 1
                    if recurrence_frequency == "every_2_days":
                        days = 2
                    elif recurrence_frequency == "weekly":
                        days = 7
                    current_departure = current_departure + timedelta(days=days)

                current_landing = current_departure + duration

        logger.info(
            f"Airline '{self.airline_company.name}' added a new flight from airport ID {origin_airport_id} to {destination_airport_id}."
        )
        return created_flights if len(created_flights) > 1 else created_flights[0]

    def update_flight(self, flight_id, update_data):
        flight = self.flight_repo.get_by_id(flight_id)
        if not flight:
            raise NotFoundError("Flight not found")

        self._validate_airline_ownership(flight)

        if flight.departure_time <= timezone.now():
            raise ValidationDomainError("Cannot modify a flight that already departed.")

        update_data.pop("recurrence_frequency", None)
        update_data.pop("recurrence_end_date", None)

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

        if "remaining_tickets" in update_data:
            update_data.pop("remaining_tickets", None)

        if "economy_seats" in update_data:
            economy_seats = update_data["economy_seats"]
            if economy_seats <= 0 or economy_seats % 6 != 0:
                raise ValidationDomainError(
                    "Economy seats must be a positive multiple of 6"
                )
            sold = flight.economy_seats - flight.remaining_economy_tickets
            if economy_seats < sold:
                raise ValidationDomainError(
                    "Economy seats cannot be lower than already sold seats"
                )

        if "business_seats" in update_data:
            business_seats = update_data["business_seats"]
            if business_seats <= 0 or business_seats % 4 != 0:
                raise ValidationDomainError(
                    "Business seats must be a positive multiple of 4"
                )
            sold = flight.business_seats - flight.remaining_business_tickets
            if business_seats < sold:
                raise ValidationDomainError(
                    "Business seats cannot be lower than already sold seats"
                )

        new_economy_seats = update_data.get("economy_seats", flight.economy_seats)
        new_business_seats = update_data.get("business_seats", flight.business_seats)

        if "economy_seats" in update_data and flight.remaining_economy_tickets > new_economy_seats:
            raise ValidationDomainError(
                "Economy seats cannot be lower than remaining economy tickets"
            )
        if "business_seats" in update_data and flight.remaining_business_tickets > new_business_seats:
            raise ValidationDomainError(
                "Business seats cannot be lower than remaining business tickets"
            )

        if "remaining_economy_tickets" in update_data:
            remaining_economy = update_data["remaining_economy_tickets"]
            if remaining_economy < 0 or remaining_economy > new_economy_seats:
                raise ValidationDomainError(
                    "remaining_economy_tickets must be between 0 and economy_seats"
                )

        if "remaining_business_tickets" in update_data:
            remaining_business = update_data["remaining_business_tickets"]
            if remaining_business < 0 or remaining_business > new_business_seats:
                raise ValidationDomainError(
                    "remaining_business_tickets must be between 0 and business_seats"
                )

        new_economy_price = update_data.get("economy_price", flight.economy_price)
        new_business_price = update_data.get("business_price", flight.business_price)
        if new_economy_price == new_business_price:
            raise ValidationDomainError(
                "Economy and business prices must be different"
            )

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

        flight.remaining_tickets = (
            flight.remaining_economy_tickets + flight.remaining_business_tickets
        )

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

        has_active_tickets = Ticket.objects.filter(
            flight_id=flight.id, status=Ticket.Status.ACTIVE
        ).exists()
        if has_active_tickets:
            raise ValidationDomainError(
                "Cannot delete flight while it has active tickets. Refund all purchased tickets first."
            )

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
