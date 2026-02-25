import apiClient from "./apiClient";

export const airlineService = {
  getMyAirlineProfile: async () => {
    const response = await apiClient.get("/accounts/airline/me/");
    return response.data;
  },

  updateMyAirlineProfile: async (payload) => {
    const response = await apiClient.patch("/accounts/airline/me/", payload);
    return response.data;
  },
};

