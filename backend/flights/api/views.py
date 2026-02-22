from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from facades.base_facade import FacadeBase
from facades.airline_facade import AirlineFacade
from .serializers import FlightSerializer


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


class AirlineFlightsAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Endpoint protejat

    def get(self, request):
        facade = AirlineFacade(request.user.username)
        flights = facade.get_my_flights()
        serializer = FlightSerializer(flights, many=True)
        return Response(serializer.data)

    def post(self, request):
        facade = AirlineFacade(request.user.username)
        serializer = FlightSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_flight = facade.add_flight(serializer.validated_data)
        return Response(
            FlightSerializer(new_flight).data, status=status.HTTP_201_CREATED
        )
