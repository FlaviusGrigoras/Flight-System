import apiClient from "./apiClient";

export const flightService = {
  getAllFlights: async () => {
    const response = await apiClient.get("/flights/");
    return response.data;
  },

  searchFlights: async ({ originCountryId, destinationCountryId, date } = {}) => {
    const params = {};
    if (originCountryId != null && originCountryId !== "")
      params.origin_country_id = originCountryId;
    if (destinationCountryId != null && destinationCountryId !== "")
      params.destination_country_id = destinationCountryId;
    if (date != null && date !== "") params.date = date;

    const response = await apiClient.get("/flights/", { params });
    return response.data;
  },

  getFlightById: async (flightId) => {
    const response = await apiClient.get(`/flights/${flightId}/`);
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
