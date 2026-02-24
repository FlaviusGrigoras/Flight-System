from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginAPIView,
    RegisterCustomerAPIView,
    RegisterAirlineAPIView,
    CurrentUserAPIView,
    AdminCustomerListAPIView,
    AdminCustomerDetailAPIView,
    AdminAirlineListAPIView,
    AdminAirlineDetailAPIView,
    AdminAdministratorListCreateAPIView,
    AdminAdministratorDetailAPIView,
)

urlpatterns = [
    # POST
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    # GET
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
    # ADMIN
    path(
        "admin/customers/",
        AdminCustomerListAPIView.as_view(),
        name="api-admin-customers",
    ),
    path(
        "admin/customers/<int:pk>/",
        AdminCustomerDetailAPIView.as_view(),
        name="api-admin-customer-detail",
    ),
    path(
        "admin/airlines/",
        AdminAirlineListAPIView.as_view(),
        name="api-admin-airlines",
    ),
    path(
        "admin/airlines/<int:pk>/",
        AdminAirlineDetailAPIView.as_view(),
        name="api-admin-airline-detail",
    ),
    path(
        "admin/administrators/",
        AdminAdministratorListCreateAPIView.as_view(),
        name="api-admin-administrators",
    ),
    path(
        "admin/administrators/<int:pk>/",
        AdminAdministratorDetailAPIView.as_view(),
        name="api-admin-administrator-detail",
    ),
]
