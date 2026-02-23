from rest_framework import serializers

from flights.models import Flight
from geo.models import Airport, Country
from accounts.models import AirlineCompany


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"
        read_only_fields = ["airline_company"]


class CountryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "iso2", "name"]


class AirportShortSerializer(serializers.ModelSerializer):
    country = CountryShortSerializer(read_only=True)

    class Meta:
        model = Airport
        fields = ["id", "iata_code", "icao_code", "name", "city", "country"]


class AirlineCompanyShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirlineCompany
        fields = ["id", "name"]


class FlightReadSerializer(serializers.ModelSerializer):
    airline_company = AirlineCompanyShortSerializer(read_only=True)
    origin_airport = AirportShortSerializer(read_only=True)
    destination_airport = AirportShortSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "airline_company",
            "origin_airport",
            "destination_airport",
            "departure_time",
            "landing_time",
            "remaining_tickets",
        ]
