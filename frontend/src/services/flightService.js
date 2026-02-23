import apiClient from "./apiClient";

export const flightService = {
  getAllFlights: async () => {
    const response = await apiClient.get("/flights/");
    return response.data;
  },
};
