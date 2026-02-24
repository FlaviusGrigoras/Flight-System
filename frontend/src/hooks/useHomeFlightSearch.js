import { useCallback, useEffect, useMemo, useState } from "react";

import { flightService } from "../services/flightService";
import { geoService } from "../services/geoService";

const getApiErrorMessage = (err, fallback) => {
  return (
    err?.response?.data?.error?.message ||
    err?.response?.data?.detail ||
    err?.response?.data?.error ||
    fallback
  );
};

const pad = (value) => String(value).padStart(2, "0");

const toLocalDateKey = (isoString) => {
  if (!isoString) return "";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "";
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
};

const estimateTicketPrice = ({ flight, passengers, cabinClass }) => {
  const departure = new Date(flight.departure_time);
  const landing = new Date(flight.landing_time);
  const durationHours = Math.max(
    1,
    (landing.getTime() - departure.getTime()) / (1000 * 60 * 60)
  );
  const scarcityFactor = Math.max(
    0,
    1 - Number(flight.remaining_tickets ?? 0) / 150
  );
  const basePrice = 45 + durationHours * 18 + scarcityFactor * 70 + (flight.id % 19);
  const classMultiplier = cabinClass === "premium" ? 1.6 : 1;
  return Math.round(basePrice * Number(passengers) * classMultiplier);
};

const uniqueById = (items) => {
  const map = new Map();
  for (const item of items) {
    if (item?.id != null && !map.has(item.id)) map.set(item.id, item);
  }
  return Array.from(map.values());
};

export function useHomeFlightSearch() {
  const [rawFlights, setRawFlights] = useState([]);
  const [airports, setAirports] = useState([]);
  const [countries, setCountries] = useState([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  const [fromAirportId, setFromAirportId] = useState("");
  const [toAirportId, setToAirportId] = useState("");
  const [departureDate, setDepartureDate] = useState("");
  const [passengers, setPassengers] = useState("1");
  const [cabinClass, setCabinClass] = useState("economy");

  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState(null);

  const refreshData = useCallback(async () => {
    setIsLoadingData(true);
    try {
      const [flightsData, airportsData, countriesData] = await Promise.all([
        flightService.getAllFlights(),
        geoService.getAirports({ limit: 5000 }),
        geoService.getCountries(),
      ]);
      setRawFlights(flightsData);
      setAirports(airportsData);
      setCountries(countriesData);
      setError(null);
    } catch (e) {
      setError(getApiErrorMessage(e, "Failed to load flights data."));
    } finally {
      setIsLoadingData(false);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const countryNameById = useMemo(() => {
    const map = new Map();
    for (const country of countries) {
      map.set(country.id, country.name);
    }
    return map;
  }, [countries]);

  const airportById = useMemo(() => {
    const map = new Map();
    for (const airport of airports) {
      map.set(airport.id, {
        ...airport,
        country_name: countryNameById.get(airport.country) ?? "Unknown country",
      });
    }
    return map;
  }, [airports, countryNameById]);

  const availableFlights = useMemo(() => {
    const now = Date.now();
    return rawFlights
      .map((flight) => ({
        ...flight,
        origin_airport_obj: airportById.get(flight.origin_airport) ?? null,
        destination_airport_obj: airportById.get(flight.destination_airport) ?? null,
      }))
      .filter((flight) => {
        const departure = new Date(flight.departure_time).getTime();
        return (
          Number.isFinite(departure) &&
          departure > now &&
          Number(flight.remaining_tickets ?? 0) > 0 &&
          flight.origin_airport_obj &&
          flight.destination_airport_obj
        );
      });
  }, [rawFlights, airportById]);

  const fromAirportOptions = useMemo(() => {
    return uniqueById(
      availableFlights.map((flight) => flight.origin_airport_obj)
    );
  }, [availableFlights]);

  const toAirportOptions = useMemo(() => {
    const flights = fromAirportId
      ? availableFlights.filter(
          (flight) => String(flight.origin_airport) === String(fromAirportId)
        )
      : availableFlights;
    return uniqueById(flights.map((flight) => flight.destination_airport_obj));
  }, [availableFlights, fromAirportId]);

  const availableDateOptions = useMemo(() => {
    const dates = new Set();
    for (const flight of availableFlights) {
      if (
        (fromAirportId && String(flight.origin_airport) !== String(fromAirportId)) ||
        (toAirportId &&
          String(flight.destination_airport) !== String(toAirportId))
      ) {
        continue;
      }
      const dateKey = toLocalDateKey(flight.departure_time);
      if (dateKey) dates.add(dateKey);
    }
    return Array.from(dates).sort();
  }, [availableFlights, fromAirportId, toAirportId]);

  useEffect(() => {
    if (!fromAirportId) return;
    const exists = fromAirportOptions.some(
      (airport) => String(airport.id) === String(fromAirportId)
    );
    if (!exists) setFromAirportId("");
  }, [fromAirportId, fromAirportOptions]);

  useEffect(() => {
    if (!toAirportId) return;
    const exists = toAirportOptions.some(
      (airport) => String(airport.id) === String(toAirportId)
    );
    if (!exists) setToAirportId("");
  }, [toAirportId, toAirportOptions]);

  useEffect(() => {
    if (!departureDate) return;
    if (!availableDateOptions.includes(departureDate)) {
      setDepartureDate("");
    }
  }, [departureDate, availableDateOptions]);

  const canSearch = Boolean(fromAirportId && toAirportId && departureDate);

  const searchFlights = useCallback(() => {
    if (!canSearch) return;

    const sorted = availableFlights
      .filter(
        (flight) =>
          String(flight.origin_airport) === String(fromAirportId) &&
          String(flight.destination_airport) === String(toAirportId) &&
          toLocalDateKey(flight.departure_time) === departureDate
      )
      .map((flight) => ({
        ...flight,
        estimated_total_price: estimateTicketPrice({
          flight,
          passengers,
          cabinClass,
        }),
      }))
      .sort((first, second) => {
        return first.estimated_total_price - second.estimated_total_price;
      });

    setResults(sorted);
    setHasSearched(true);
  }, [
    availableFlights,
    canSearch,
    cabinClass,
    departureDate,
    fromAirportId,
    passengers,
    toAirportId,
  ]);

  return {
    fromAirportId,
    setFromAirportId,
    toAirportId,
    setToAirportId,
    departureDate,
    setDepartureDate,
    passengers,
    setPassengers,
    cabinClass,
    setCabinClass,
    fromAirportOptions,
    toAirportOptions,
    availableDateOptions,
    isLoadingData,
    error,
    canSearch,
    results,
    hasSearched,
    searchFlights,
    refreshData,
  };
}

