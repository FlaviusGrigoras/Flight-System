from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken
from facades.anonymous_facade import AnonymousFacade
from facades.administrator_facade import AdministratorFacade
from core.exceptions import ForbiddenError
from .serializers import (
    LoginRequestSerializer,
    CustomerRegistrationSerializer,
    AirlineRegistrationSerializer,
    CurrentUserSerializer,
    CustomerAdminSerializer,
    AirlineAdminSerializer,
    AirlineMeSerializer,
    AdministratorReadSerializer,
    AdministratorCreateSerializer,
)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        facade = AnonymousFacade()
        user = facade.login(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        refresh = RefreshToken.for_user(user)
        user_data = CurrentUserSerializer(user, context={"request": request}).data

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
        facade = AnonymousFacade()

        username = facade.generate_unique_username_from_email(data["email"])
        user_data = {
            "username": username,
            "password": data["password"],
            "email": data["email"],
        }

        customer_data = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
        }

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
        serializer = CurrentUserSerializer(request.user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirlineMeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_airline(self, request):
        if not hasattr(request.user, "airline_profile"):
            raise ForbiddenError("User is not an airline company")
        return request.user.airline_profile

    def get(self, request):
        airline = self._get_airline(request)
        return Response(
            AirlineMeSerializer(airline, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        airline = self._get_airline(request)
        serializer = AirlineMeSerializer(
            airline, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminCustomerListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facade = AdministratorFacade(request.user)
        customers = facade.get_all_customers()
        serializer = CustomerAdminSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminCustomerDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk: int):
        facade = AdministratorFacade(request.user)
        facade.remove_customer(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminAirlineListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facade = AdministratorFacade(request.user)
        airlines = facade.get_all_airlines()
        serializer = AirlineAdminSerializer(airlines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AirlineRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        facade = AdministratorFacade(request.user)

        user_data = {
            "username": data["username"],
            "password": data["password"],
            "email": data["email"],
        }
        airline_data = {
            "name": data["name"],
            "country_id": data["country_id"],
        }

        airline = facade.add_airline(user_data, airline_data)
        return Response(
            AirlineAdminSerializer(airline).data,
            status=status.HTTP_201_CREATED,
        )


class AdminAirlineDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk: int):
        facade = AdministratorFacade(request.user)
        facade.remove_airline(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminAdministratorListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facade = AdministratorFacade(request.user)
        administrators = facade.get_all_administrators()
        serializer = AdministratorReadSerializer(administrators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AdministratorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        facade = AdministratorFacade(request.user)

        username = data.get("username") or facade.generate_unique_username_from_email(
            data["email"]
        )
        user_data = {
            "username": username,
            "password": data["password"],
            "email": data["email"],
        }
        admin_data = {"first_name": data["first_name"], "last_name": data["last_name"]}

        new_admin = facade.add_administrator(user_data, admin_data)

        return Response(
            AdministratorReadSerializer(new_admin).data, status=status.HTTP_201_CREATED
        )


class AdminAdministratorDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk: int):
        facade = AdministratorFacade(request.user)
        facade.remove_administrator(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
