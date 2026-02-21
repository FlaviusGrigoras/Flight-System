from django.urls import path
from .views import LoginAPIView, RegisterCustomerAPIView, RegisterAirlineAPIView

urlpatterns = [
    # POST
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path(
        "register/customer/",
        RegisterCustomerAPIView.as_view(),
        name="api-register-customer",
    ),
    path(
        "register/airline/",
        RegisterAirlineAPIView.as_view(),
        name="api-register-airline",
    ),
]
