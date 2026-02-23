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

    def purchase_ticket(self, flight_id):
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

            existing_ticket = Ticket.objects.filter(
                flight=flight, customer=self.customer
            ).exists()

            if existing_ticket:
                raise ValidationDomainError(
                    "You already purchased a ticket for this flight"
                )

            flight.remaining_tickets -= 1
            self.flight_repo.update(flight)

            ticket = Ticket(flight=flight, customer=self.customer)
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

            ticket.flight.remaining_tickets += 1
            self.flight_repo.update(ticket.flight)

            logger.info(
                f"Customer '{self.customer.first_name} {self.customer.last_name}' cancelled ticket ID {ticket.id} for flight ID {ticket.flight.id}."
            )

            return ticket
