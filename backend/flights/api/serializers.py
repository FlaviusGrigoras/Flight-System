from rest_framework import serializers

from flights.models import Flight


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"
        read_only_fields = ["airline_company"]
