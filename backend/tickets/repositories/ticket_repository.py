from core.repository import BaseRepository
from tickets.models import Ticket


class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

    def get_tickets_by_customer(self, customer_id):
        return self.model.objects.select_related(
            "flight", "flight__origin_airport", "flight__destination_airport"
        ).filter(customer_id=customer_id)
