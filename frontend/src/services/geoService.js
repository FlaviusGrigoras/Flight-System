import apiClient from "./apiClient";

export const geoService = {
  getCountries: async () => {
    const response = await apiClient.get("/geo/countries/");
    return response.data;
  },

  getAirports: async ({ countryId, countryIso2, q, limit } = {}) => {
    const params = {};
    if (countryId != null && countryId !== "") params.country_id = countryId;
    if (countryIso2 != null && countryIso2 !== "") params.country_iso2 = countryIso2;
    if (q != null && q !== "") params.q = q;
    if (limit != null && limit !== "") params.limit = limit;

    const response = await apiClient.get("/geo/airports/", { params });
    return response.data;
  },
};

