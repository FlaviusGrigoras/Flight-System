import { useCallback, useEffect, useMemo, useState } from "react";

import { useAuth } from "../context/AuthContext";
import { flightService } from "../services/flightService";
import { ticketService } from "../services/ticketService";

const getApiErrorMessage = (err, fallback) => {
  return (
    err?.response?.data?.error?.message ||
    err?.response?.data?.detail ||
    err?.response?.data?.error ||
    fallback
  );
};

export function useCustomerDashboard() {
  const { user, isLoading } = useAuth();
  const isCustomer = user?.role === "customer";

  const [tickets, setTickets] = useState([]);
  const [isLoadingTickets, setIsLoadingTickets] = useState(false);

  const [flightById, setFlightById] = useState({});
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  const refreshTickets = useCallback(async () => {
    setIsLoadingTickets(true);
    try {
      const data = await ticketService.getMyTickets();
      setTickets(data);
      setError(null);
    } catch (e) {
      setError(getApiErrorMessage(e, "Failed to load tickets."));
    } finally {
      setIsLoadingTickets(false);
    }
  }, []);

  useEffect(() => {
    if (!isCustomer) return;
    refreshTickets();
  }, [isCustomer, refreshTickets]);

  const cancelTicket = useCallback(
    async (ticketId) => {
      clearMessages();
      try {
        const updated = await ticketService.cancelMyTicket(ticketId);
        setSuccess(`Ticket #${ticketId} cancelled.`);
        setTickets((prev) =>
          prev.map((t) => (t.id === ticketId ? updated : t))
        );
      } catch (e) {
        setError(getApiErrorMessage(e, "Failed to cancel ticket."));
      }
    },
    [clearMessages]
  );

  const ticketFlightIds = useMemo(() => {
    const ids = new Set();
    for (const ticket of tickets) {
      if (ticket?.flight != null) ids.add(ticket.flight);
    }
    return Array.from(ids);
  }, [tickets]);

  useEffect(() => {
    let cancelled = false;

    const fetchTicketFlights = async () => {
      if (!isCustomer) return;
      if (ticketFlightIds.length === 0) {
        setFlightById({});
        return;
      }

      try {
        const pairs = await Promise.all(
          ticketFlightIds.map(async (id) => {
            try {
              const flight = await flightService.getFlightById(id);
              return [id, flight];
            } catch {
              return [id, null];
            }
          })
        );
        const map = Object.fromEntries(pairs.filter(([, value]) => value != null));
        if (!cancelled) setFlightById(map);
      } catch {
      }
    };

    fetchTicketFlights();
    return () => {
      cancelled = true;
    };
  }, [isCustomer, ticketFlightIds]);

  return {
    user,
    isLoading,
    isCustomer,
    error,
    success,
    clearMessages,
    tickets,
    isLoadingTickets,
    refreshTickets,
    cancelTicket,
    flightById,
  };
}

