import { useCallback, useEffect, useMemo, useState } from "react";

import { flightService } from "../services/flightService";

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
  const classMultiplier = cabinClass === "business" ? 1.6 : 1;
  return Math.round(basePrice * Number(passengers) * classMultiplier);
};

const uniqueById = (items) => {
  const map = new Map();
  for (const item of items) {
    if (item?.id != null && !map.has(item.id)) map.set(item.id, item);
  }
  return Array.from(map.values());
};

const normalizeAirportObject = (airport) => {
  if (!airport || typeof airport !== "object") return null;
  const countryName =
    (typeof airport.country?.name === "string" && airport.country.name.trim()) ||
    (typeof airport.country_name === "string" && airport.country_name.trim()) ||
    "Unknown country";
  return {
    ...airport,
    country_name: countryName,
  };
};

const fallbackAirportObject = (airportId) => {
  if (airportId == null || airportId === "") return null;
  const id = Number(airportId);
  const normalizedId = Number.isFinite(id) ? id : airportId;
  return {
    id: normalizedId,
    name: `Airport #${normalizedId}`,
    city: `Airport #${normalizedId}`,
    iata_code: "",
    icao_code: "",
    country_name: "Unknown country",
  };
};

export function useHomeFlightSearch() {
  const [rawFlights, setRawFlights] = useState([]);
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
      const flightsData = await flightService.getAllFlights();
      setRawFlights(flightsData);
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

  const availableFlights = useMemo(() => {
    const now = Date.now();
    return rawFlights
      .map((flight) => {
        const originAirport =
          normalizeAirportObject(flight.origin_airport_obj) ??
          fallbackAirportObject(flight.origin_airport);
        const destinationAirport =
          normalizeAirportObject(flight.destination_airport_obj) ??
          fallbackAirportObject(flight.destination_airport);
        return {
          ...flight,
          origin_airport_obj: originAirport,
          destination_airport_obj: destinationAirport,
        };
      })
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
  }, [rawFlights]);

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
