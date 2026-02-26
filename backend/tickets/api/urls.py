from django.urls import path

from .views import (
    TicketPurchaseAPIView,
    MyTicketsAPIView,
    TicketCancelAPIView,
    AirlineSoldTicketsAPIView,
    AdminTicketsAPIView,
    TicketRefundAPIView,
)

urlpatterns = [
    path("purchase/", TicketPurchaseAPIView.as_view(), name="ticket-purchase"),
    path("my-tickets/", MyTicketsAPIView.as_view(), name="my-tickets"),
    path(
        "my-tickets/<int:pk>/cancel/",
        TicketCancelAPIView.as_view(),
        name="ticket-cancel",
    ),
    path("airline/sold/", AirlineSoldTicketsAPIView.as_view(), name="airline-sold"),
    path("admin/all/", AdminTicketsAPIView.as_view(), name="admin-tickets"),
    path("<int:pk>/refund/", TicketRefundAPIView.as_view(), name="ticket-refund"),
]
