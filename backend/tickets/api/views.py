from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from facades.airline_facade import AirlineFacade
from facades.customer_facade import CustomerFacade
from .serializers import TicketSerializer, TicketSoldSerializer


class TicketPurchaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        flight_id = request.data.get("flight_id")
        cabin_class = request.data.get("cabin_class")
        if not flight_id:
            return Response(
                {"error": "flight_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            flight_id = int(flight_id)
        except (TypeError, ValueError):
            return Response(
                {"error": "flight_id must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        facade = CustomerFacade(request.user)
        ticket = facade.purchase_ticket(flight_id, cabin_class=cabin_class)

        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


class MyTicketsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facade = CustomerFacade(request.user)
        tickets = facade.get_my_tickets()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


class TicketCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        facade = CustomerFacade(request.user)
        ticket = facade.cancel_ticket(pk)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)


class AirlineSoldTicketsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        flight_id = request.query_params.get("flight_id")
        if flight_id is not None:
            if not str(flight_id).isdigit():
                return Response(
                    {"error": "flight_id must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            flight_id = int(flight_id)

        facade = AirlineFacade(request.user.username)
        tickets = facade.get_sold_tickets(flight_id=flight_id)
        return Response(TicketSoldSerializer(tickets, many=True).data)
