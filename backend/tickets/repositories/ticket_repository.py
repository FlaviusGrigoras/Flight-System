from core.repository import BaseRepository
from tickets.models import Ticket
from django.db import connection, DatabaseError
from django.db.models import Case, IntegerField, Value, When


class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

    def get_tickets_by_customer(self, customer_id):
        queryset = self.model.objects.select_related(
            "flight",
            "flight__origin_airport",
            "flight__destination_airport",
        )

        try:
            if connection.vendor == "postgresql":
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM get_tickets_by_customer(%s);",
                        [customer_id],
                    )
                    rows = cursor.fetchall()
                ticket_ids = [row[0] for row in rows]
                if not ticket_ids:
                    return queryset.none()
                ordering = Case(
                    *[
                        When(id=ticket_id, then=Value(index))
                        for index, ticket_id in enumerate(ticket_ids)
                    ],
                    output_field=IntegerField(),
                )
                return queryset.filter(id__in=ticket_ids).order_by(ordering)
        except DatabaseError:
            pass

        return queryset.filter(customer_id=customer_id)

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

        return qs.order_by("-purchased_at", "-id")

    def get_all_tickets(self, flight_id=None, airline_company_id=None, status=None):
        qs = self.model.objects.select_related(
            "customer",
            "customer__user",
            "flight",
            "flight__airline_company",
            "flight__origin_airport",
            "flight__origin_airport__country",
            "flight__destination_airport",
            "flight__destination_airport__country",
        )

        if flight_id is not None:
            qs = qs.filter(flight_id=flight_id)
        if airline_company_id is not None:
            qs = qs.filter(flight__airline_company_id=airline_company_id)
        if status is not None:
            qs = qs.filter(status=status)

        return qs.order_by("-purchased_at", "-id")
