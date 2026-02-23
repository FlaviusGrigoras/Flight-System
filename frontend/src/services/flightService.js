import apiClient from "./apiClient";

export const flightService = {
  getAllFlights: async () => {
    const response = await apiClient.get("/flights/");
    return response.data;
  },

  getMyFlights: async () => {
    const response = await apiClient.get("/flights/my-flights/");
    return response.data;
  },

  createFlight: async (payload) => {
    const response = await apiClient.post("/flights/my-flights/", payload);
    return response.data;
  },

  updateMyFlight: async (flightId, payload) => {
    const response = await apiClient.patch(`/flights/my-flights/${flightId}/`, payload);
    return response.data;
  },

  deleteMyFlight: async (flightId) => {
    const response = await apiClient.delete(`/flights/my-flights/${flightId}/`);
    return response.data;
  },
};
