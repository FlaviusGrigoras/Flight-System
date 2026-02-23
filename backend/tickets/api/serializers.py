from rest_framework import serializers

from tickets.models import Ticket
from accounts.models import Customer
from flights.models import Flight
from flights.api.serializers import FlightReadSerializer


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class CustomerShortSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "username", "email"]


class TicketSoldSerializer(serializers.ModelSerializer):
    flight = FlightReadSerializer(read_only=True)
    customer = CustomerShortSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "flight", "customer", "status", "purchased_at", "seat_no"]
