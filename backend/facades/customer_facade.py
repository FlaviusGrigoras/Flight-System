from facades.base_facade import FacadeBase
from tickets.repositories.ticket_repository import TicketRepository
from tickets.models import Ticket
from core.exceptions import ValidationDomainError, NotFoundError
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger("tickets")


class CustomerFacade(FacadeBase):
    def __init__(self, user):
        super().__init__()
        self.ticket_repo = TicketRepository()
        self.customer = self.customer_repo.get_customer_by_username(user.username)

    def _assign_seat_no(self, flight, cabin_class):
        if cabin_class == Ticket.CabinClass.BUSINESS:
            seats_per_row = 4
            letters = ["A", "B", "C", "D"]
        else:
            seats_per_row = 6
            letters = ["A", "B", "C", "D", "E", "F"]

        sold_count = (
            Ticket.objects.filter(flight=flight, cabin_class=cabin_class)
            .exclude(status=Ticket.Status.CANCELLED)
            .count()
        )
        index = sold_count + 1
        row = (index - 1) // seats_per_row + 1
        letter = letters[(index - 1) % seats_per_row]
        return f"{row}{letter}"

    def purchase_ticket(self, flight_id, cabin_class=None):
        if not self.customer:
            raise ValidationDomainError("User is not a customer")

        with transaction.atomic():
            flight = self.flight_repo.get_by_id(flight_id)

            if not flight:
                raise NotFoundError("Flight not found")

            if flight.departure_time <= timezone.now():
                raise ValidationDomainError("Cannot purchase tickets for past flights")

            if flight.remaining_tickets <= 0:
                raise ValidationDomainError("No tickets available for this flight")

            if flight.economy_seats == 0 and flight.business_seats == 0:
                flight.economy_seats = flight.remaining_tickets
                flight.remaining_economy_tickets = flight.remaining_tickets
                flight.remaining_business_tickets = 0

            cabin_value = (cabin_class or Ticket.CabinClass.ECONOMY).upper()
            if cabin_value not in Ticket.CabinClass.values:
                raise ValidationDomainError("Invalid cabin class")

            if cabin_value == Ticket.CabinClass.BUSINESS:
                if flight.remaining_business_tickets <= 0:
                    raise ValidationDomainError(
                        "No business tickets available for this flight"
                    )
                flight.remaining_business_tickets -= 1
            else:
                if flight.remaining_economy_tickets <= 0:
                    raise ValidationDomainError(
                        "No economy tickets available for this flight"
                    )
                flight.remaining_economy_tickets -= 1

            existing_ticket = Ticket.objects.filter(
                flight=flight, customer=self.customer
            ).exists()

            if existing_ticket:
                raise ValidationDomainError(
                    "You already purchased a ticket for this flight"
                )

            flight.remaining_tickets = (
                flight.remaining_economy_tickets + flight.remaining_business_tickets
            )
            self.flight_repo.update(flight)

            ticket = Ticket(
                flight=flight,
                customer=self.customer,
                cabin_class=cabin_value,
                seat_no=self._assign_seat_no(flight, cabin_value),
            )
            self.ticket_repo.add(ticket)

            logger.info(
                f"Customer '{self.customer.first_name} {self.customer.last_name}' successfully purchased a ticket for flight ID {flight.id}."
            )

            return ticket

    def get_my_tickets(self):
        if not self.customer:
            return []
        return self.ticket_repo.get_tickets_by_customer(self.customer.id)

    def cancel_ticket(self, ticket_id):
        if not self.customer:
            raise ValidationDomainError("User is not a customer")

        with transaction.atomic():
            ticket = Ticket.objects.select_related("flight").filter(
                id=ticket_id, customer_id=self.customer.id
            ).first()
            if not ticket:
                raise NotFoundError("Ticket not found")

            if ticket.status == Ticket.Status.CANCELLED:
                raise ValidationDomainError("Ticket already cancelled")

            if ticket.flight.departure_time <= timezone.now():
                raise ValidationDomainError("Cannot cancel ticket after departure")

            ticket.status = Ticket.Status.CANCELLED
            ticket.cancelled_at = timezone.now()
            ticket.save(update_fields=["status", "cancelled_at"])

            if ticket.cabin_class == Ticket.CabinClass.BUSINESS:
                ticket.flight.remaining_business_tickets += 1
            else:
                ticket.flight.remaining_economy_tickets += 1
            ticket.flight.remaining_tickets = (
                ticket.flight.remaining_economy_tickets
                + ticket.flight.remaining_business_tickets
            )
            self.flight_repo.update(ticket.flight)

            logger.info(
                f"Customer '{self.customer.first_name} {self.customer.last_name}' cancelled ticket ID {ticket.id} for flight ID {ticket.flight.id}."
            )

            return ticket
