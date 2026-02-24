from flights.models import Flight
from django.db import connection, DatabaseError
from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone
from datetime import timedelta


class FlightRepository:
    def _with_related(self):
        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        )

    def _get_flights_within_next_12_hours(self, *, country_id, field_name):
        now = timezone.now()
        limit = now + timedelta(hours=12)
        return self._with_related().filter(
            **{
                f"{field_name}__country_id": country_id,
                f"{'landing_time' if field_name == 'destination_airport' else 'departure_time'}__range": (
                    now,
                    limit,
                ),
            }
        )

    def _get_flights_using_stored_function(self, function_name, country_id):
        if connection.vendor != "postgresql":
            raise DatabaseError("Stored function support is enabled only on PostgreSQL")

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT id FROM {function_name}(%s);", [country_id])
            rows = cursor.fetchall()

        flight_ids = [row[0] for row in rows]
        if not flight_ids:
            return self._with_related().none()

        ordering = Case(
            *[When(id=flight_id, then=Value(index)) for index, flight_id in enumerate(flight_ids)],
            output_field=IntegerField(),
        )
        return self._with_related().filter(id__in=flight_ids).order_by(ordering)

    def get_by_id(self, flight_id):
        return self._with_related().filter(id=flight_id).first()

    def get_all(self):
        return self._with_related().all()

    def add(self, flight):
        flight.save()
        return flight

    def update(self, flight):
        flight.save()
        return flight

    def delete(self, flight_id):
        Flight.objects.filter(id=flight_id).delete()

    def get_flights_by_origin_country(self, country_id):
        return self._with_related().filter(origin_airport__country_id=country_id)

    def get_flights_by_destination_country(self, country_id):
        return self._with_related().filter(destination_airport__country_id=country_id)

    def get_flights_by_departure_time(self, date):
        return Flight.objects.filter(departure_time__date=date)

    def get_flights_by_landing_time(self, date):
        return Flight.objects.filter(landing_time__date=date)

    def get_flights_by_airline_id(self, airline_id):
        return self._with_related().filter(airline_company_id=airline_id)

    def get_arrival_flights(self, country_id):
        try:
            return self._get_flights_using_stored_function(
                "get_arrival_flights", country_id
            )
        except DatabaseError:
            return self._get_flights_within_next_12_hours(
                country_id=country_id, field_name="destination_airport"
            )

    def get_departure_flights(self, country_id):
        try:
            return self._get_flights_using_stored_function(
                "get_departure_flights", country_id
            )
        except DatabaseError:
            return self._get_flights_within_next_12_hours(
                country_id=country_id, field_name="origin_airport"
            )

    def get_flights_by_parameters(
        self, origin_country_id, destination_country_id, target_date
    ):
        return self._with_related().filter(
            origin_airport__country_id=origin_country_id,
            destination_airport__country_id=destination_country_id,
            departure_time__date=target_date,
        )
