from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from facades.base_facade import FacadeBase
from facades.airline_facade import AirlineFacade
from .serializers import FlightSerializer


class FlightListAPIView(APIView):
    def get(self, request):
        facade = FacadeBase()
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
