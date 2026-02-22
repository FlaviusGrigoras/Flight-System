from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .serializers import CountrySerializer, AirportSerializer
from facades.base_facade import FacadeBase
from geo.models import Airport


class CountryListAPIView(APIView):
    def get(self, request):
        facade = FacadeBase()
        countries = facade.get_all_countries()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirportListAPIView(APIView):
    def get(self, request):
        country_id = request.query_params.get("country_id")

        airports = Airport.objects.select_related("country").all()
        if country_id is not None:
            if not country_id.isdigit():
                raise ValidationError({"country_id": "country_id must be an integer"})
            airports = airports.filter(country_id=int(country_id))

        serializer = AirportSerializer(airports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
