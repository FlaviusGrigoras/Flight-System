import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import CheckoutCard from "../components/CheckoutCard/CheckoutCard";
import { useAuth } from "../context/AuthContext";
import { flightService } from "../services/flightService";

const normalizeCabinClass = (value) => {
  if (!value) return "ECONOMY";
  const normalized = String(value).trim().toUpperCase();
  if (normalized === "BUSINESS") return "BUSINESS";
  return "ECONOMY";
};

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

const getApiErrorMessage = (err, fallback) =>
  err?.response?.data?.error?.message ||
  err?.response?.data?.detail ||
  err?.response?.data?.error ||
  fallback;

const formatCardNumber = (input) =>
  input
    .replace(/\D/g, "")
    .slice(0, 19)
    .replace(/(.{4})/g, "$1 ")
    .trim();

const formatCvv = (input) => input.replace(/\D/g, "").slice(0, 4);

const EXPIRY_MONTH_OPTIONS = Array.from({ length: 12 }, (_, index) => {
  const month = String(index + 1).padStart(2, "0");
  return { value: month, label: month };
});

const CURRENT_YEAR = new Date().getFullYear();
const EXPIRY_YEAR_OPTIONS = Array.from({ length: 15 }, (_, index) => {
  const year = String(CURRENT_YEAR + index);
  return { value: year, label: year };
});

const isLuhnValid = (cardDigits) => {
  if (!/^\d{12,19}$/.test(cardDigits)) return false;

  let sum = 0;
  let shouldDouble = false;
  for (let i = cardDigits.length - 1; i >= 0; i -= 1) {
    let digit = Number(cardDigits[i]);
    if (shouldDouble) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    sum += digit;
    shouldDouble = !shouldDouble;
  }
  return sum % 10 === 0;
};

export default function BuyPage() {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const [flight, setFlight] = useState(null);
  const [isLoadingFlight, setIsLoadingFlight] = useState(true);
  const [error, setError] = useState(null);

  const [selectedCabinClass, setSelectedCabinClass] = useState(
    normalizeCabinClass(location.state?.cabinClass),
  );
  const [ticketQuantity, setTicketQuantity] = useState(1);
  const [cardNumberInput, setCardNumberInput] = useState("");
  const [expiryMonth, setExpiryMonth] = useState("");
  const [expiryYear, setExpiryYear] = useState("");
  const [cvvInput, setCvvInput] = useState("");
  const [cardTouched, setCardTouched] = useState(false);
  const [expiryMonthTouched, setExpiryMonthTouched] = useState(false);
  const [expiryYearTouched, setExpiryYearTouched] = useState(false);
  const [cvvTouched, setCvvTouched] = useState(false);

  const isCustomer = user?.role === "customer";
  const isAuthenticated = Boolean(user);

  const loadFlight = async () => {
    setIsLoadingFlight(true);
    try {
      const data = await flightService.getFlightById(flightId);
      setFlight(data);
      setError(null);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load flight details."));
    } finally {
      setIsLoadingFlight(false);
    }
  };

  useEffect(() => {
    loadFlight();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [flightId]);

  const economyRemaining = Number(flight?.remaining_economy_tickets ?? 0);
  const businessRemaining = Number(flight?.remaining_business_tickets ?? 0);
  const selectedRemaining =
    selectedCabinClass === "BUSINESS" ? businessRemaining : economyRemaining;

  useEffect(() => {
    if (
      selectedCabinClass === "ECONOMY" &&
      economyRemaining <= 0 &&
      businessRemaining > 0
    ) {
      setSelectedCabinClass("BUSINESS");
    }
    if (
      selectedCabinClass === "BUSINESS" &&
      businessRemaining <= 0 &&
      economyRemaining > 0
    ) {
      setSelectedCabinClass("ECONOMY");
    }
  }, [selectedCabinClass, economyRemaining, businessRemaining]);

  useEffect(() => {
    if (ticketQuantity > selectedRemaining && selectedRemaining > 0) {
      setTicketQuantity(selectedRemaining);
    }
    if (selectedRemaining === 0 && ticketQuantity !== 1) {
      setTicketQuantity(1);
    }
  }, [ticketQuantity, selectedRemaining]);

  const quantityOptions = useMemo(() => {
    const max = Math.max(1, Math.min(selectedRemaining, 9));
    return Array.from({ length: max }, (_, index) => index + 1);
  }, [selectedRemaining]);

  const cardDigits = cardNumberInput.replace(/\D/g, "");
  const isCardValid = isLuhnValid(cardDigits);
  const isExpiryMonthValid = /^(0[1-9]|1[0-2])$/.test(expiryMonth);
  const isExpiryYearValid = EXPIRY_YEAR_OPTIONS.some(
    (yearOption) => yearOption.value === expiryYear,
  );
  const isCvvValid = /^\d{3,4}$/.test(cvvInput);

  const unitPrice =
    selectedCabinClass === "BUSINESS"
      ? Number(flight?.business_price ?? 0)
      : Number(flight?.economy_price ?? 0);
  const totalPrice = unitPrice * Number(ticketQuantity);

  const canContinue =
    isCustomer &&
    flight &&
    !isLoadingFlight &&
    selectedRemaining > 0 &&
    ticketQuantity > 0 &&
    ticketQuantity <= selectedRemaining &&
    isCardValid &&
    isExpiryMonthValid &&
    isExpiryYearValid &&
    isCvvValid;

  const handleContinueToPayment = () => {
    setCardTouched(true);
    setExpiryMonthTouched(true);
    setExpiryYearTouched(true);
    setCvvTouched(true);
    if (!canContinue) return;

    navigate(`/buy/${flightId}/processing`, {
      state: {
        checkout: {
          flightId: Number(flightId),
          cabinClass: selectedCabinClass,
          quantity: Number(ticketQuantity),
          cardLast4: cardDigits.slice(-4),
          flight,
        },
      },
    });
  };

  return (
    <Container maxWidth="md" sx={{ py: 5 }}>
      <Typography variant="h4" gutterBottom>
        Checkout
      </Typography>

      <Typography variant="body1" gutterBottom>
        Selected flight: #{flightId}
      </Typography>

      {isLoadingFlight && (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
          <CircularProgress size={20} />
          <Typography>Loading flight details...</Typography>
        </Box>
      )}

      {!isAuthenticated && (
        <Alert severity="info" sx={{ mb: 2 }}>
          You need to log in as a customer to continue checkout.
        </Alert>
      )}

      {isAuthenticated && !isCustomer && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Only customer accounts can complete checkout.
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!isLoadingFlight && flight && (
        <Stack spacing={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Flight details
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                Airline: {flight.airline_company_name || "Airline"}
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                Route: Airport #{flight.origin_airport} → Airport #
                {flight.destination_airport}
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                Departure: {formatDateTime(flight.departure_time)}
              </Typography>
              <Typography variant="body2">
                Landing: {formatDateTime(flight.landing_time)}
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Ticket options
              </Typography>

              <Stack spacing={2}>
                <FormControl fullWidth>
                  <InputLabel id="buy-cabin-class-label">
                    Cabin class
                  </InputLabel>
                  <Select
                    labelId="buy-cabin-class-label"
                    label="Cabin class"
                    value={selectedCabinClass}
                    onChange={(event) =>
                      setSelectedCabinClass(
                        normalizeCabinClass(event.target.value),
                      )
                    }
                  >
                    <MenuItem value="ECONOMY" disabled={economyRemaining <= 0}>
                      Economy ({economyRemaining} left) -{" "}
                      {formatPrice(flight.economy_price)}
                    </MenuItem>
                    <MenuItem
                      value="BUSINESS"
                      disabled={businessRemaining <= 0}
                    >
                      Business ({businessRemaining} left) -{" "}
                      {formatPrice(flight.business_price)}
                    </MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel id="buy-quantity-label">
                    Number of tickets
                  </InputLabel>
                  <Select
                    labelId="buy-quantity-label"
                    label="Number of tickets"
                    value={ticketQuantity}
                    onChange={(event) =>
                      setTicketQuantity(Number(event.target.value))
                    }
                  >
                    {quantityOptions.map((qty) => (
                      <MenuItem key={qty} value={qty}>
                        {qty}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Typography variant="body2" color="text.secondary">
                  Total: {formatPrice(totalPrice)}
                </Typography>
              </Stack>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Payment details
              </Typography>
              <TextField
                fullWidth
                label="Card number"
                value={cardNumberInput}
                onChange={(event) =>
                  setCardNumberInput(formatCardNumber(event.target.value))
                }
                onBlur={() => setCardTouched(true)}
                placeholder="1234 5678 9012 3456"
                error={cardTouched && !isCardValid}
                helperText={
                  cardTouched && !isCardValid
                    ? "Enter a valid card number."
                    : "Card is validated by standard checksum."
                }
              />
              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={2}
                sx={{ mt: 2 }}
              >
                <TextField
                  fullWidth
                  select
                  label="Expiry month"
                  value={expiryMonth}
                  onChange={(event) => setExpiryMonth(event.target.value)}
                  onBlur={() => setExpiryMonthTouched(true)}
                  error={expiryMonthTouched && !isExpiryMonthValid}
                  helperText={
                    expiryMonthTouched && !isExpiryMonthValid
                      ? "Select a valid month."
                      : "Month on card."
                  }
                >
                  {EXPIRY_MONTH_OPTIONS.map((monthOption) => (
                    <MenuItem key={monthOption.value} value={monthOption.value}>
                      {monthOption.label}
                    </MenuItem>
                  ))}
                </TextField>

                <TextField
                  fullWidth
                  select
                  label="Expiry year"
                  value={expiryYear}
                  onChange={(event) => setExpiryYear(event.target.value)}
                  onBlur={() => setExpiryYearTouched(true)}
                  error={expiryYearTouched && !isExpiryYearValid}
                  helperText={
                    expiryYearTouched && !isExpiryYearValid
                      ? "Select a valid year."
                      : "Year on card."
                  }
                >
                  {EXPIRY_YEAR_OPTIONS.map((yearOption) => (
                    <MenuItem key={yearOption.value} value={yearOption.value}>
                      {yearOption.label}
                    </MenuItem>
                  ))}
                </TextField>

                <TextField
                  fullWidth
                  label="CVV"
                  value={cvvInput}
                  onChange={(event) =>
                    setCvvInput(formatCvv(event.target.value))
                  }
                  onBlur={() => setCvvTouched(true)}
                  inputProps={{
                    inputMode: "numeric",
                    pattern: "[0-9]*",
                    maxLength: 4,
                  }}
                  error={cvvTouched && !isCvvValid}
                  helperText={
                    cvvTouched && !isCvvValid
                      ? "Enter 3 or 4 digits."
                      : "Security code on card."
                  }
                />
              </Stack>
            </CardContent>
          </Card>
        </Stack>
      )}

      <Stack direction="row" spacing={1} sx={{ mt: 3 }}>
        {!isAuthenticated && (
          <Button variant="contained" onClick={() => navigate("/login")}>
            Go to login
          </Button>
        )}
        <div
          onClick={handleContinueToPayment}
          disabled={!canContinue}
          style={{ display: "inline-block" }}
        >
          <CheckoutCard />
        </div>
        <Button variant="outlined" onClick={() => navigate("/")}>
          Back to search
        </Button>
      </Stack>
    </Container>
  );
}
