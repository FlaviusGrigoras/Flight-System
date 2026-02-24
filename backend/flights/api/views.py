from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from core.exceptions import ForbiddenError
from facades.base_facade import FacadeBase
from facades.airline_facade import AirlineFacade
from .serializers import FlightSerializer, FlightReadSerializer


class FlightListAPIView(APIView):
    def get(self, request):
        facade = FacadeBase()

        origin_country_id = request.query_params.get("origin_country_id")
        destination_country_id = request.query_params.get("destination_country_id")
        target_date = request.query_params.get("date")

        filters = [origin_country_id, destination_country_id, target_date]
        if any(filters) and not all(filters):
            raise ValidationError(
                {
                    "filters": (
                        "origin_country_id, destination_country_id and date are "
                        "required together."
                    )
                }
            )

        if all(filters):
            if not origin_country_id.isdigit() or not destination_country_id.isdigit():
                raise ValidationError(
                    {"filters": "country ids must be integers."}
                )
            parsed_date = parse_date(target_date)
            if parsed_date is None:
                raise ValidationError({"date": "Invalid date format. Use YYYY-MM-DD."})

            flights = facade.get_flights_by_parameters(
                origin_country_id=int(origin_country_id),
                destination_country_id=int(destination_country_id),
                date=parsed_date,
            )
        else:
            flights = facade.get_all_flights()

        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data)


class FlightDetailAPIView(APIView):
    def get(self, request, pk):
        facade = FacadeBase()
        flight = facade.get_flight_by_id(pk)
        if not flight:
            return Response(
                {"error": "Flight not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(FlightSerializer(flight).data)


class ArrivalFlightsAPIView(APIView):
    def get(self, request):
        country_id = request.query_params.get("country_id")
        if not country_id or not country_id.isdigit():
            raise ValidationError({"country_id": "country_id must be an integer"})

        facade = FacadeBase()
        flights = facade.get_arrival_flights(int(country_id))
        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DepartureFlightsAPIView(APIView):
    def get(self, request):
        country_id = request.query_params.get("country_id")
        if not country_id or not country_id.isdigit():
            raise ValidationError({"country_id": "country_id must be an integer"})

        facade = FacadeBase()
        flights = facade.get_departure_flights(int(country_id))
        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirlineFlightsAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Endpoint protejat

    def get(self, request):
        facade = AirlineFacade(request.user.username)
        flights = facade.get_my_flights()
        serializer = FlightReadSerializer(flights, many=True)
        return Response(serializer.data)

    def post(self, request):
        facade = AirlineFacade(request.user.username)
        serializer = FlightSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_flight = facade.add_flight(serializer.validated_data)
        return Response(
            FlightReadSerializer(new_flight).data, status=status.HTTP_201_CREATED
        )


class AirlineFlightDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_airline_facade(self, request):
        facade = AirlineFacade(request.user.username)
        if not facade.airline_company:
            raise ForbiddenError("User is not an airline company")
        return facade

    def get(self, request, pk: int):
        facade = self._get_airline_facade(request)
        flight = facade.get_flight_by_id(pk)
        if not flight:
            return Response(
                {"error": "Flight not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if flight.airline_company_id != facade.airline_company.id:
            raise ForbiddenError("You can only manage your own flights")
        return Response(FlightReadSerializer(flight).data)

    def patch(self, request, pk: int):
        facade = self._get_airline_facade(request)
        serializer = FlightSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = facade.update_flight(pk, serializer.validated_data)
        return Response(FlightReadSerializer(updated).data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        facade = self._get_airline_facade(request)
        facade.remove_flight(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
