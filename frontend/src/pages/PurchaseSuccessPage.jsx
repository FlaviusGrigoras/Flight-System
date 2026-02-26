import { useEffect, useMemo } from "react";
import { Button, Card, CardContent, Container, Stack, Typography } from "@mui/material";
import { useLocation, useNavigate, useParams } from "react-router-dom";

const formatDateTime = (value) => {
  if (!value) return "N/A";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "N/A";
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

const formatPrice = (value) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "N/A";
  return `EUR ${numeric.toFixed(2)}`;
};

export default function PurchaseSuccessPage() {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const result = location.state?.result;
  const checkout = result?.checkout;
  const tickets = result?.tickets ?? [];
  const flight = checkout?.flight;

  const totalPrice = useMemo(() => {
    if (!flight) return null;
    const cabinClass = checkout?.cabinClass;
    const quantity = Number(checkout?.quantity ?? 1);
    const unitPrice =
      cabinClass === "BUSINESS"
        ? Number(flight.business_price ?? 0)
        : Number(flight.economy_price ?? 0);
    return unitPrice * quantity;
  }, [checkout?.cabinClass, checkout?.quantity, flight]);

  useEffect(() => {
    if (!result) {
      navigate(`/buy/${flightId}`, { replace: true });
    }
  }, [flightId, navigate, result]);

  if (!result) return null;

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h4" gutterBottom>
        Thank you, this is your flight detail
      </Typography>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Stack spacing={1}>
            <Typography variant="h6">
              {flight?.airline_company_name || "Airline"}
            </Typography>
            <Typography variant="body2">
              Flight ID: #{checkout?.flightId}
            </Typography>
            <Typography variant="body2">
              Route: Airport #{flight?.origin_airport} → Airport #
              {flight?.destination_airport}
            </Typography>
            <Typography variant="body2">
              Departure: {formatDateTime(flight?.departure_time)}
            </Typography>
            <Typography variant="body2">
              Landing: {formatDateTime(flight?.landing_time)}
            </Typography>
            <Typography variant="body2">
              Cabin class: {checkout?.cabinClass}
            </Typography>
            <Typography variant="body2">
              Tickets: {checkout?.quantity}
            </Typography>
            <Typography variant="body2">
              Paid with card ending in: **** {checkout?.cardLast4 || "N/A"}
            </Typography>
            <Typography variant="body2">
              Total paid: {formatPrice(totalPrice)}
            </Typography>
          </Stack>
        </CardContent>
      </Card>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Issued tickets
          </Typography>
          <Stack spacing={0.5}>
            {tickets.map((ticket) => (
              <Typography key={ticket.id} variant="body2">
                Ticket #{ticket.id}
                {ticket.seat_no ? ` - Seat ${ticket.seat_no}` : ""}
              </Typography>
            ))}
          </Stack>
        </CardContent>
      </Card>

      <Stack direction="row" spacing={1}>
        <Button
          variant="contained"
          onClick={() => navigate("/customer/dashboard")}
        >
          Go to my tickets
        </Button>
        <Button variant="outlined" onClick={() => navigate("/")}>
          Back to home
        </Button>
      </Stack>
    </Container>
  );
}
