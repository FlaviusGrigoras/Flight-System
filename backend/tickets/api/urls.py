from django.urls import path

from .views import TicketPurchaseAPIView, MyTicketsAPIView

urlpatterns = [
    path("purchase/", TicketPurchaseAPIView.as_view(), name="ticket-purchase"),
    path("my-tickets/", MyTicketsAPIView.as_view(), name="my-tickets"),
]
