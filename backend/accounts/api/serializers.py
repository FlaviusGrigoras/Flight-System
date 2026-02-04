from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
        ]

    def validate(self, data):
        errors = {}

        if data.get("password1") != data.get("password2"):
            errors["password"] = "Passwords do not match"
        if not data.get("first_name"):
            errors["first_name"] = "First name is mandatory"
        if not data.get("last_name"):
            errors["last_name"] = "Last name is mandatory"

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        password = validated_data.get("password1")

        validated_data.pop("password1", None)
        validated_data.pop("password2", None)

        user = User.objects.create_user(password=password, **validated_data)

        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError(
                "Both username and password are required."
            )

        data["user"] = user
        return data
