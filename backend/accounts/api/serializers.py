from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import AirlineCompany
from geo.models import Country

User = get_user_model()


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class CustomerRegistrationSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    email = serializers.EmailField(required=True)

    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value


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

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_country_id(self, value):
        if not Country.objects.filter(id=value).exists():
            raise serializers.ValidationError("Country does not exist.")
        return value


class CurrentUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]

    def get_role(self, obj):
        if hasattr(obj, "admin_profile"):
            return "administrator"
        if hasattr(obj, "airline_profile"):
            return "airline"
        if hasattr(obj, "customer_profile"):
            return "customer"
        return "anonymous"
