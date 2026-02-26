import base64

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
    address = serializers.CharField(max_length=100, required=True)
    phone_no = serializers.CharField(max_length=15, required=True)
    credit_card_no = serializers.CharField(max_length=13, required=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_phone_no(self, value):
        value = value.strip()
        if Customer.objects.filter(phone_no=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_credit_card_no(self, value):
        value = value.strip()
        if Customer.objects.filter(credit_card_no=value).exists():
            raise serializers.ValidationError("Credit card number already exists.")
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
        if obj.user_role:
            role = obj.user_role.role_name.strip().lower()
            if role.startswith("administrator"):
                return "administrator"
            if role.startswith("airline"):
                return "airline"
            if role.startswith("customer"):
                return "customer"
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
        logo_url = airline.get_logo_url(request=request)
        return {"id": airline.id, "name": airline.name, "logo_url": logo_url}


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_superuser", "is_staff"]


class CustomerAdminSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "address",
            "phone_no",
            "credit_card_no",
            "user",
        ]


class AirlineAdminSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    country_name = serializers.CharField(source="country.name", read_only=True)
    country_iso2 = serializers.CharField(source="country.iso2", read_only=True)

    class Meta:
        model = AirlineCompany
        fields = ["id", "name", "country", "country_name", "country_iso2", "user"]


class AirlineMeSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(write_only=True, required=False, allow_null=True)
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
        request = self.context.get("request")
        return obj.get_logo_url(request=request)

    @staticmethod
    def _file_to_data_url(uploaded_file):
        content = uploaded_file.read()
        encoded = base64.b64encode(content).decode("ascii")
        mime_type = (
            getattr(uploaded_file, "content_type", None) or "application/octet-stream"
        )
        return f"data:{mime_type};base64,{encoded}"

    def update(self, instance, validated_data):
        logo_file = validated_data.pop("logo", serializers.empty)
        instance = super().update(instance, validated_data)

        if logo_file is not serializers.empty:
            instance.logo = (
                None if logo_file is None else self._file_to_data_url(logo_file)
            )
            instance.save(update_fields=["logo"])

        return instance


class CustomerMeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "address",
            "phone_no",
            "credit_card_no",
            "email",
        ]

    def validate_phone_no(self, value):
        value = value.strip()
        qs = Customer.objects.filter(phone_no=value)
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_credit_card_no(self, value):
        value = value.strip()
        qs = Customer.objects.filter(credit_card_no=value)
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Credit card number already exists.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        customer_user_id = self.instance.user_id if self.instance else None
        if User.objects.filter(email__iexact=value).exclude(id=customer_user_id).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None) or {}
        email = user_data.get("email")
        if email and instance.user.email != email:
            instance.user.email = email
            instance.user.save(update_fields=["email"])

        return super().update(instance, validated_data)


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
