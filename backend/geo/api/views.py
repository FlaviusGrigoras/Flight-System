from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CountrySerializer
from facades.base_facade import FacadeBase

class CountryListAPIView(APIView):
    def get(self, request):
        facade=FacadeBase()
        countries=facade.get_all_countries()
        serializer=CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)