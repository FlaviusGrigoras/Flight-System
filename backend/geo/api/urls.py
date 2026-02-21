from django.urls import path
from geo.api.views import CountryListAPIView

urlpatterns = [
    path("countries/", CountryListAPIView.as_view(), name="api-countries"),
]
