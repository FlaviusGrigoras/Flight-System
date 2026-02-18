from flights.models import Flight
from django.utils import timezone
from datetime import timedelta


class FlightRepository:
    def get_by_id(self, flight_id):
        return (
            Flight.objects.select_related(
                "airline_company",
                "origin_airport__country",
                "destination_airport__country",
            )
            .filter(id=flight_id)
            .first()
        )

    def get_all(self):
        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        ).all()

    def add(self, flight):
        flight.save()
        return flight

    def update(self, flight):
        flight.save()
        return flight

    def delete(self, flight_id):
        Flight.objects.filter(id=flight_id).delete()

    def get_flights_by_origin_country(self, country_id):
        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        ).filter(origin_airport__country_id=country_id)

    def get_flights_by_destination_country(self, country_id):
        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        ).filter(destination_airport__country_id=country_id)

    def get_flights_by_departure_time(self, date):
        return Flight.objects.filter(departure_time__date=date)

    def get_flights_by_landing_time(self, date):
        return Flight.objects.filter(landing_time__date=date)

    def get_flights_by_airline_id(self, airline_id):
        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        ).filter(airline_company_id=airline_id)

    def get_arrival_flights(self, country_id):
        now = timezone.now()
        limit = now + timedelta(hours=12)

        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        ).filter(
            destination_airport__country_id=country_id,
            landing_time__range=(now, limit),
        )

    def get_departure_flights(self, country_id):
        now = timezone.now()
        limit = now + timedelta(hours=12)

        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        ).filter(
            origin_airport__country_id=country_id,
            departure_time__range=(now, limit),
        )

    def get_flights_by_parameters(
        self, origin_country_id, destination_country_id, target_date
    ):
        return Flight.objects.select_related(
            "airline_company",
            "origin_airport__country",
            "destination_airport__country",
        ).filter(
            origin_airport__country_id=origin_country_id,
            destination_airport__country_id=destination_country_id,
            departure_time__date=target_date,
        )
