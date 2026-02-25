import apiClient from "./apiClient";

export const adminService = {
  getCustomers: async () => {
    const response = await apiClient.get("/accounts/admin/customers/");
    return response.data;
  },

  deleteCustomer: async (customerId) => {
    const response = await apiClient.delete(`/accounts/admin/customers/${customerId}/`);
    return response.data;
  },

  getAirlines: async () => {
    const response = await apiClient.get("/accounts/admin/airlines/");
    return response.data;
  },

  createAirline: async (payload) => {
    const response = await apiClient.post("/accounts/admin/airlines/", payload);
    return response.data;
  },

  deleteAirline: async (airlineId) => {
    const response = await apiClient.delete(`/accounts/admin/airlines/${airlineId}/`);
    return response.data;
  },

  getAdministrators: async () => {
    const response = await apiClient.get("/accounts/admin/administrators/");
    return response.data;
  },

  createAdministrator: async (payload) => {
    const response = await apiClient.post("/accounts/admin/administrators/", payload);
    return response.data;
  },

  deleteAdministrator: async (administratorId) => {
    const response = await apiClient.delete(
      `/accounts/admin/administrators/${administratorId}/`
    );
    return response.data;
  },
};
