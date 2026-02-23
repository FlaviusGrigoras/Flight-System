from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from facades.anonymous_facade import AnonymousFacade
from .serializers import (
    LoginRequestSerializer,
    CustomerRegistrationSerializer,
    AirlineRegistrationSerializer,
    CurrentUserSerializer,
)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        facade = AnonymousFacade()
        user = facade.login(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        refresh = RefreshToken.for_user(user)
        user_data = CurrentUserSerializer(user).data

        return Response(
            {
                "message": "Login successful",
                "user": user_data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_200_OK,
        )


class RegisterCustomerAPIView(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user_data = {
            "username": data["username"],
            "password": data["password"],
            "email": data["email"],
        }

        customer_data = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "address": data["address"],
            "phone_no": data["phone_no"],
        }

        facade = AnonymousFacade()
        customer = facade.add_customer(user_data, customer_data)

        return Response(
            {"message": "Customer created succesfully", "customer_id": customer.id},
            status=status.HTTP_201_CREATED,
        )


class RegisterAirlineAPIView(APIView):
    def post(self, request):
        serializer = AirlineRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        user_data = {
            "username": data["username"],
            "password": data["password"],
            "email": data["email"],
        }
        airline_data = {
            "name": data["name"],
            "country_id": data["country_id"],
        }

        facade = AnonymousFacade()
        airline = facade.add_airline(user_data, airline_data)

        return Response(
            {"message": "Airline created successfully", "airline_id": airline.id},
            status=status.HTTP_201_CREATED,
        )


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
