import apiClient from "./apiClient";

export const ticketService = {
  purchaseTicket: async (flightId) => {
    const response = await apiClient.post("/tickets/purchase/", {
      flight_id: flightId,
    });
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
};
