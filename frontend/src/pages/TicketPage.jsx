import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Button,
  CircularProgress,
  Container,
  Stack,
  Typography,
} from "@mui/material";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import TicketDesign from "../components/ticketDesign/ticketDesign";
import { useAuth } from "../context/AuthContext";
import { flightService } from "../services/flightService";
import { ticketService } from "../services/ticketService";

const getApiErrorMessage = (err, fallback) =>
  err?.response?.data?.error?.message ||
  err?.response?.data?.detail ||
  err?.response?.data?.error ||
  fallback;

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

const getAirportLabel = (airport) => {
  if (!airport) return "N/A";
  const code = airport.iata_code || airport.icao_code || "N/A";
  const city = airport.city || airport.name || "";
  return city ? `${code} (${city})` : code;
};

export default function TicketPage() {
  const { ticketId } = useParams();
  const parsedTicketId = Number(ticketId);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isLoading: isAuthLoading } = useAuth();
  const isCustomer = user?.role === "customer";

  const initialTicket = useMemo(() => {
    const candidate = location.state?.ticket;
    if (!candidate) return null;
    return Number(candidate.id) === parsedTicketId ? candidate : null;
  }, [location.state, parsedTicketId]);

  const initialFlight = useMemo(() => {
    const candidate = location.state?.flight;
    if (!candidate) return null;
    return candidate;
  }, [location.state]);

  const [ticket, setTicket] = useState(initialTicket);
  const [flight, setFlight] = useState(initialFlight);
  const [isLoadingTicket, setIsLoadingTicket] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setTicket(initialTicket);
    setFlight(initialFlight);
  }, [initialTicket, initialFlight]);

  useEffect(() => {
    let cancelled = false;

    const loadTicket = async () => {
      if (!isCustomer) return;
      if (!Number.isInteger(parsedTicketId) || parsedTicketId <= 0) return;

      const hasTicket = ticket && Number(ticket.id) === parsedTicketId;
      const hasFlight =
        hasTicket &&
        flight &&
        Number(flight.id) === Number(ticket.flight ?? initialFlight?.id);
      if (hasTicket && hasFlight) return;

      setIsLoadingTicket(true);
      try {
        let resolvedTicket = hasTicket ? ticket : null;
        if (!resolvedTicket) {
          const myTickets = await ticketService.getMyTickets();
          resolvedTicket =
            myTickets.find((item) => Number(item.id) === parsedTicketId) ?? null;
        }
        if (!resolvedTicket) {
          throw new Error("TICKET_NOT_FOUND");
        }

        const flightId = Number(resolvedTicket.flight);
        let resolvedFlight =
          flight && Number(flight.id) === flightId ? flight : initialFlight;
        if (!resolvedFlight || Number(resolvedFlight.id) !== flightId) {
          resolvedFlight = await flightService.getFlightById(flightId);
        }

        if (!cancelled) {
          setTicket(resolvedTicket);
          setFlight(resolvedFlight);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          if (err?.message === "TICKET_NOT_FOUND") {
            setError("Ticket not found or you do not have access to it.");
          } else {
            setError(getApiErrorMessage(err, "Failed to load ticket details."));
          }
          setTicket(null);
          setFlight(null);
        }
      } finally {
        if (!cancelled) setIsLoadingTicket(false);
      }
    };

    loadTicket();
    return () => {
      cancelled = true;
    };
  }, [flight, initialFlight, isCustomer, parsedTicketId, ticket]);

  if (isAuthLoading) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  if (!user) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          Please log in to view this ticket.
        </Alert>
        <Button variant="contained" onClick={() => navigate("/login")}>
          Go to login
        </Button>
      </Container>
    );
  }

  if (!isCustomer) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Alert severity="warning">
          This page is available only for customer accounts.
        </Alert>
      </Container>
    );
  }

  if (!Number.isInteger(parsedTicketId) || parsedTicketId <= 0) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Invalid ticket id in URL.
        </Alert>
        <Button variant="contained" onClick={() => navigate("/customer/dashboard")}>
          Back to dashboard
        </Button>
      </Container>
    );
  }

  if (isLoadingTicket && (!ticket || !flight)) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <CircularProgress size={20} />
          <Typography>Loading ticket details...</Typography>
        </Stack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={() => navigate("/customer/dashboard")}>
          Back to dashboard
        </Button>
      </Container>
    );
  }

  const originAirport = flight?.origin_airport_obj ?? flight?.origin_airport;
  const destinationAirport =
    flight?.destination_airport_obj ?? flight?.destination_airport;

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h5" gutterBottom>
        Ticket #{ticket?.id}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Airline: {flight?.airline_company_name || flight?.airline_company?.name || "N/A"}
      </Typography>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          marginBottom: 24,
          backgroundColor: "#e8e8e8",
          borderRadius: 16,
          padding: 16,
        }}
      >
        <TicketDesign
          ticket={ticket}
          flight={flight}
          passengerName={user?.display_name || user?.username}
        />
      </div>

      <Stack spacing={0.5} sx={{ mb: 3 }}>
        <Typography variant="body2">
          Route: {getAirportLabel(originAirport)} → {getAirportLabel(destinationAirport)}
        </Typography>
        <Typography variant="body2">
          Departure: {formatDateTime(flight?.departure_time)}
        </Typography>
        <Typography variant="body2">Landing: {formatDateTime(flight?.landing_time)}</Typography>
        <Typography variant="body2">
          Purchased: {formatDateTime(ticket?.purchased_at)}
        </Typography>
      </Stack>

      <Stack direction="row" spacing={1}>
        <Button variant="contained" onClick={() => navigate("/customer/dashboard")}>
          Back to dashboard
        </Button>
        <Button variant="outlined" onClick={() => navigate("/")}>
          Back to home
        </Button>
      </Stack>
    </Container>
  );
}
