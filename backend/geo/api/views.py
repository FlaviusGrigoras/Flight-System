from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .serializers import CountrySerializer, AirportSerializer
from facades.base_facade import FacadeBase


class CountryListAPIView(APIView):
    def get(self, request):
        facade = FacadeBase()
        countries = facade.get_all_countries()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AirportListAPIView(APIView):
    def get(self, request):
        facade = FacadeBase()
        country_id = request.query_params.get("country_id")
        country_iso2 = request.query_params.get("country_iso2")
        query = (request.query_params.get("q") or "").strip()
        limit = request.query_params.get("limit")
        country_id_value = None
        country_iso2_value = None
        limit_value = None

        if country_id is not None:
            if not country_id.isdigit():
                raise ValidationError({"country_id": "country_id must be an integer"})
            country_id_value = int(country_id)

        if country_iso2 is not None:
            normalized_iso2 = country_iso2.strip().upper()
            if len(normalized_iso2) != 2:
                raise ValidationError(
                    {"country_iso2": "country_iso2 must be a 2-letter ISO code"}
                )
            country_iso2_value = normalized_iso2

        if limit is not None:
            if not str(limit).isdigit():
                raise ValidationError({"limit": "limit must be an integer"})
            parsed_limit = int(limit)
            if parsed_limit < 1 or parsed_limit > 5000:
                raise ValidationError({"limit": "limit must be between 1 and 5000"})
            limit_value = parsed_limit

        airports = facade.search_airports(
            country_id=country_id_value,
            country_iso2=country_iso2_value,
            query=query,
            limit=limit_value,
        )

        serializer = AirportSerializer(airports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
