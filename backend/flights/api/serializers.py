from rest_framework import serializers

from flights.models import Flight
from geo.models import Airport, Country
from accounts.models import AirlineCompany


class FlightSerializer(serializers.ModelSerializer):
    recurrence_frequency = serializers.ChoiceField(
        choices=["daily", "every_2_days", "weekly", "monthly"],
        required=False,
        allow_null=True,
        write_only=True,
    )
    recurrence_end_date = serializers.DateField(
        required=False, allow_null=True, write_only=True
    )
    origin_airport_obj = serializers.SerializerMethodField(read_only=True)
    destination_airport_obj = serializers.SerializerMethodField(read_only=True)

    def _serialize_airport(self, airport):
        if airport is None:
            return None
        return AirportShortSerializer(airport).data

    def get_origin_airport_obj(self, obj):
        return self._serialize_airport(getattr(obj, "origin_airport", None))

    def get_destination_airport_obj(self, obj):
        return self._serialize_airport(getattr(obj, "destination_airport", None))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        airline = getattr(instance, "airline_company", None)
        data["airline_company_name"] = getattr(airline, "name", "") or ""
        request = self.context.get("request")
        data["airline_logo_url"] = (
            airline.get_logo_url(request=request) if airline is not None else None
        )
        return data

    class Meta:
        model = Flight
        fields = "__all__"
        read_only_fields = [
            "airline_company",
            "remaining_tickets",
        ]
        extra_kwargs = {
            "economy_seats": {"required": True},
            "business_seats": {"required": True},
            "economy_price": {"required": True},
            "business_price": {"required": True},
            "origin_airport": {"required": True},
            "destination_airport": {"required": True},
            "departure_time": {"required": True},
            "landing_time": {"required": True},
        }


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
    logo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AirlineCompany
        fields = ["id", "name", "logo_url"]

    def get_logo_url(self, obj):
        request = self.context.get("request")
        return obj.get_logo_url(request=request)


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
            "economy_seats",
            "business_seats",
            "remaining_economy_tickets",
            "remaining_business_tickets",
            "economy_price",
            "business_price",
        ]
