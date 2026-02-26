import apiClient from "./apiClient";

export const ticketService = {
  purchaseTicket: async (flightId, cabinClass) => {
    const payload = {
      flight_id: flightId,
    };
    if (cabinClass) {
      payload.cabin_class = String(cabinClass).toUpperCase();
    }

    const response = await apiClient.post("/tickets/purchase/", payload);
    return response.data;
  },

  getMyTickets: async () => {
    const response = await apiClient.get("/tickets/my-tickets/");
    return response.data;
  },

  cancelMyTicket: async (ticketId) => {
    const response = await apiClient.post(`/tickets/my-tickets/${ticketId}/cancel/`);
    return response.data;
  },

  getAirlineSoldTickets: async ({ flightId } = {}) => {
    const params = {};
    if (flightId != null && flightId !== "") params.flight_id = flightId;
    const response = await apiClient.get("/tickets/airline/sold/", { params });
    return response.data;
  },

  getAdminTickets: async ({ flightId, airlineId, status } = {}) => {
    const params = {};
    if (flightId != null && flightId !== "") params.flight_id = flightId;
    if (airlineId != null && airlineId !== "") params.airline_id = airlineId;
    if (status != null && status !== "") params.status = status;
    const response = await apiClient.get("/tickets/admin/all/", { params });
    return response.data;
  },

  refundTicket: async (ticketId) => {
    const response = await apiClient.post(`/tickets/${ticketId}/refund/`);
    return response.data;
  },
};
