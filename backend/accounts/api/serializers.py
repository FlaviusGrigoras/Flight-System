from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import AirlineCompany, Administrator, Customer
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


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_superuser", "is_staff"]


class CustomerAdminSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "user"]


class AirlineAdminSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    country_name = serializers.CharField(source="country.name", read_only=True)
    country_iso2 = serializers.CharField(source="country.iso2", read_only=True)

    class Meta:
        model = AirlineCompany
        fields = ["id", "name", "country", "country_name", "country_iso2", "user"]


class AdministratorReadSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Administrator
        fields = ["id", "first_name", "last_name", "user"]


class AdministratorCreateSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=False,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value
