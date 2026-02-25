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
    display_name = serializers.SerializerMethodField()
    airline_company = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "display_name", "airline_company"]

    def get_role(self, obj):
        if obj.is_superuser or hasattr(obj, "admin_profile"):
            return "administrator"
        if hasattr(obj, "airline_profile"):
            return "airline"
        if hasattr(obj, "customer_profile"):
            return "customer"
        return "anonymous"

    def get_display_name(self, obj):
        if hasattr(obj, "airline_profile"):
            return obj.airline_profile.name
        if hasattr(obj, "customer_profile"):
            return f"{obj.customer_profile.first_name} {obj.customer_profile.last_name}"
        if hasattr(obj, "admin_profile"):
            return f"{obj.admin_profile.first_name} {obj.admin_profile.last_name}"
        return obj.username

    def get_airline_company(self, obj):
        if not hasattr(obj, "airline_profile"):
            return None
        airline = obj.airline_profile
        request = self.context.get("request")
        logo_url = None
        if airline.logo:
            if request is not None:
                logo_url = request.build_absolute_uri(airline.logo.url)
            else:
                logo_url = airline.logo.url
        return {"id": airline.id, "name": airline.name, "logo_url": logo_url}


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


class AirlineMeSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source="country.name", read_only=True)
    country_iso2 = serializers.CharField(source="country.iso2", read_only=True)
    logo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AirlineCompany
        fields = [
            "id",
            "name",
            "country",
            "country_name",
            "country_iso2",
            "website",
            "logo",
            "logo_url",
        ]

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url


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
