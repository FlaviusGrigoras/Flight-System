from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginAPIView,
    RegisterCustomerAPIView,
    RegisterAirlineAPIView,
    CurrentUserAPIView,
)

urlpatterns = [
    # POST
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("me/", CurrentUserAPIView.as_view(), name="api-me"),
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
