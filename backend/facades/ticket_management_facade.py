import logging

from django.db import transaction
from django.utils import timezone

from core.exceptions import ForbiddenError, NotFoundError, ValidationDomainError
from facades.base_facade import FacadeBase
from tickets.models import Ticket
from tickets.repositories.ticket_repository import TicketRepository

logger = logging.getLogger("tickets")


class TicketManagementFacade(FacadeBase):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.ticket_repo = TicketRepository()
        self.airline_company = None
        if user and getattr(user, "is_authenticated", False):
            self.airline_company = self.airline_repo.get_airline_by_username(
                user.username
            )

    def _get_ticket_for_update(self, ticket_id: int) -> Ticket:
        ticket = (
            Ticket.objects.select_related(
                "flight",
                "flight__airline_company",
                "flight__origin_airport",
                "flight__destination_airport",
                "customer",
                "customer__user",
            )
            .filter(id=ticket_id)
            .first()
        )
        if not ticket:
            raise NotFoundError("Ticket not found")
        return ticket

    @staticmethod
    def _validate_ticket_can_be_refunded(ticket: Ticket):
        if ticket.status == Ticket.Status.REFUNDED:
            raise ValidationDomainError("Ticket already refunded")
        if ticket.status == Ticket.Status.CANCELLED:
            raise ValidationDomainError("Cancelled tickets cannot be refunded")
        if ticket.status != Ticket.Status.ACTIVE:
            raise ValidationDomainError("Only active tickets can be refunded")
        if ticket.flight.departure_time <= timezone.now():
            raise ValidationDomainError("Cannot refund ticket after departure")

    def _refund_ticket(self, ticket: Ticket) -> Ticket:
        self._validate_ticket_can_be_refunded(ticket)

        ticket.status = Ticket.Status.REFUNDED
        ticket.refunded_at = timezone.now()
        ticket.save(update_fields=["status", "refunded_at"])

        if ticket.cabin_class == Ticket.CabinClass.BUSINESS:
            ticket.flight.remaining_business_tickets += 1
        else:
            ticket.flight.remaining_economy_tickets += 1
        ticket.flight.remaining_tickets = (
            ticket.flight.remaining_economy_tickets
            + ticket.flight.remaining_business_tickets
        )
        self.flight_repo.update(ticket.flight)
        return ticket

    def refund_ticket_as_airline(self, ticket_id: int) -> Ticket:
        if not self.airline_company:
            raise ForbiddenError("User is not an airline company")

        with transaction.atomic():
            ticket = self._get_ticket_for_update(ticket_id)
            if ticket.flight.airline_company_id != self.airline_company.id:
                raise ForbiddenError("You can only refund tickets for your own flights")
            refunded = self._refund_ticket(ticket)

        logger.info(
            "Airline '%s' refunded ticket ID %s for flight ID %s.",
            self.airline_company.name,
            refunded.id,
            refunded.flight_id,
        )
        return refunded

    def refund_ticket_as_admin(self, ticket_id: int) -> Ticket:
        if not self.user or not self.user.is_superuser:
            raise ForbiddenError("Access restricted to administrators only")

        with transaction.atomic():
            ticket = self._get_ticket_for_update(ticket_id)
            refunded = self._refund_ticket(ticket)

        logger.info(
            "Administrator '%s' refunded ticket ID %s for flight ID %s.",
            self.user.username,
            refunded.id,
            refunded.flight_id,
        )
        return refunded

    def get_all_tickets_for_admin(
        self, *, flight_id=None, airline_id=None, status=None
    ):
        if not self.user or not self.user.is_superuser:
            raise ForbiddenError("Access restricted to administrators only")

        normalized_status = None
        if status:
            normalized_status = str(status).strip().upper()
            if normalized_status not in Ticket.Status.values:
                raise ValidationDomainError("Invalid status filter")

        return self.ticket_repo.get_all_tickets(
            flight_id=flight_id,
            airline_company_id=airline_id,
            status=normalized_status,
        )
