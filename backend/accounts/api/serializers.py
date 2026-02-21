from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import AirlineCompany, Customer
from geo.models import Country

User = get_user_model()


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class CustomerRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=50,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    email = serializers.EmailField(required=True)

    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    address = serializers.CharField(max_length=100, required=True)
    phone_no = serializers.CharField(
        max_length=15,
        required=True,
        validators=[UniqueValidator(queryset=Customer.objects.all())],
    )
    credit_card_no = serializers.CharField(
        max_length=13,
        required=True,
        validators=[UniqueValidator(queryset=Customer.objects.all())],
    )


class AirlineRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    email = serializers.EmailField(required=True)

    name = serializers.CharField(
        max_length=100,
        required=True,
        validators=[UniqueValidator(queryset=AirlineCompany.objects.all())],
    )
    country_id = serializers.IntegerField(required=True)

    def validate_country_id(self, value):
        if not Country.objects.filter(id=value).exists():
            raise serializers.ValidationError("Country does not exist.")
        return value
