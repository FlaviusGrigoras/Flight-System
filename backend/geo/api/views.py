from django.db.models import Q
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
        country_iso2 = request.query_params.get("country_iso2")
        query = (request.query_params.get("q") or "").strip()
        limit = request.query_params.get("limit")

        airports = Airport.objects.select_related("country").all()

        if country_id is not None:
            if not country_id.isdigit():
                raise ValidationError({"country_id": "country_id must be an integer"})
            airports = airports.filter(country_id=int(country_id))

        if country_iso2 is not None:
            normalized_iso2 = country_iso2.strip().upper()
            if len(normalized_iso2) != 2:
                raise ValidationError(
                    {"country_iso2": "country_iso2 must be a 2-letter ISO code"}
                )
            airports = airports.filter(country__iso2=normalized_iso2)

        if query:
            airports = airports.filter(
                Q(name__icontains=query)
                | Q(city__icontains=query)
                | Q(iata_code__icontains=query)
                | Q(icao_code__icontains=query)
            )

        if limit is not None:
            if not str(limit).isdigit():
                raise ValidationError({"limit": "limit must be an integer"})
            limit_value = int(limit)
            if limit_value < 1 or limit_value > 5000:
                raise ValidationError({"limit": "limit must be between 1 and 5000"})
            airports = airports[:limit_value]

        serializer = AirportSerializer(airports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
