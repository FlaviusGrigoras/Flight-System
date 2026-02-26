import { useEffect, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Stack,
  Typography,
} from "@mui/material";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { ticketService } from "../services/ticketService";

const getApiErrorMessage = (err, fallback) =>
  err?.response?.data?.error?.message ||
  err?.response?.data?.detail ||
  err?.response?.data?.error ||
  fallback;

export default function PaymentProcessingPage() {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const checkout = location.state?.checkout;

  const [secondsLeft, setSecondsLeft] = useState(3);
  const [isProcessing, setIsProcessing] = useState(true);
  const [error, setError] = useState(null);
  const hasSubmittedRef = useRef(false);

  useEffect(() => {
    if (!checkout) {
      navigate(`/buy/${flightId}`, { replace: true });
    }
  }, [checkout, flightId, navigate]);

  useEffect(() => {
    if (!checkout || secondsLeft <= 0) return undefined;
    const timer = window.setTimeout(
      () => setSecondsLeft((prev) => Math.max(0, prev - 1)),
      1000
    );
    return () => window.clearTimeout(timer);
  }, [checkout, secondsLeft]);

  useEffect(() => {
    if (!checkout || secondsLeft > 0 || hasSubmittedRef.current) return;
    hasSubmittedRef.current = true;

    const processPayment = async () => {
      try {
        const quantity = Math.max(1, Number(checkout.quantity) || 1);
        const tickets = [];
        for (let i = 0; i < quantity; i += 1) {
          // Backend purchase endpoint creates one ticket per call.
          // We call it multiple times to match selected quantity.
          const ticket = await ticketService.purchaseTicket(
            checkout.flightId,
            checkout.cabinClass
          );
          tickets.push(ticket);
        }

        navigate(`/buy/${flightId}/success`, {
          replace: true,
          state: { result: { checkout, tickets } },
        });
      } catch (err) {
        setError(getApiErrorMessage(err, "Payment failed. Please try again."));
        setIsProcessing(false);
      }
    };

    processPayment();
  }, [checkout, flightId, navigate, secondsLeft]);

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Stack spacing={2} alignItems="center">
        <Typography variant="h4">Communicating with bank</Typography>
        {isProcessing && (
          <>
            <CircularProgress />
            <Typography variant="body1">
              Please wait... {secondsLeft}s
            </Typography>
          </>
        )}

        {error && (
          <Alert severity="error" sx={{ width: "100%" }}>
            {error}
          </Alert>
        )}

        {!isProcessing && (
          <Box sx={{ width: "100%", display: "flex", justifyContent: "center" }}>
            <Button variant="contained" onClick={() => navigate(`/buy/${flightId}`)}>
              Back to checkout
            </Button>
          </Box>
        )}
      </Stack>
    </Container>
  );
}
