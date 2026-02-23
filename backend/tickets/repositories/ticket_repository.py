from core.repository import BaseRepository
from tickets.models import Ticket


class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

    def get_tickets_by_customer(self, customer_id):
        return self.model.objects.select_related(
            "flight", "flight__origin_airport", "flight__destination_airport"
        ).filter(customer_id=customer_id)

    def get_tickets_by_airline(self, airline_company_id, flight_id=None):
        qs = self.model.objects.select_related(
            "customer",
            "customer__user",
            "flight",
            "flight__airline_company",
            "flight__origin_airport",
            "flight__origin_airport__country",
            "flight__destination_airport",
            "flight__destination_airport__country",
        ).filter(flight__airline_company_id=airline_company_id)

        if flight_id is not None:
            qs = qs.filter(flight_id=flight_id)

        return qs
