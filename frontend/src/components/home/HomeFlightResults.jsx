import { Box, Button, Paper, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

import styles from "./HomeFlightSearchSection.module.css";

const formatLocalTime = (isoString) => {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "--:--";
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
};

const getAirlineId = (airlineCompany) => {
  if (airlineCompany && typeof airlineCompany === "object")
    return airlineCompany.id;
  return airlineCompany;
};

const getAirlineLogoUrl = (flight) => {
  if (flight.airline_company?.logo_url) return flight.airline_company.logo_url;
  if (flight.airline_logo_url) return flight.airline_logo_url;
  return null;
};

const getAirlineName = (flight) => {
  if (flight.airline_company?.name?.trim())
    return flight.airline_company.name.trim();
  if (
    typeof flight.airline_company_name === "string" &&
    flight.airline_company_name.trim()
  ) {
    return flight.airline_company_name.trim();
  }
  if (typeof flight.airline_name === "string" && flight.airline_name.trim()) {
    return flight.airline_name.trim();
  }
  return "Companie aeriana";
};

const airportCode = (airport) => {
  const iata = airport?.iata_code?.trim()?.toUpperCase();
  if (iata && iata.length === 3) return iata;
  const fallback = airport?.icao_code?.trim()?.toUpperCase();
  if (fallback && fallback.length >= 3) return fallback.slice(0, 3);
  return "N/A";
};

const airportCity = (airport) => {
  const city = airport?.city?.trim();
  if (city) return city;
  const name = airport?.name?.trim();
  if (name) return name;
  return "Unknown city";
};

const airportLabel = (airport) =>
  `${airportCode(airport)} - ${airportCity(airport)}`;

const airlineBadge = (airlineCompany) => {
  const airlineId = getAirlineId(airlineCompany);
  return airlineId != null && airlineId !== "" ? `A${airlineId}` : "AL";
};

export default function HomeFlightResults({ flights, passengers, cabinClass }) {
  const navigate = useNavigate();

  return (
    <Box className={styles.resultsList}>
      {flights.map((flight) => {
        const origin = flight.origin_airport_obj;
        const destination = flight.destination_airport_obj;
        const airlineName = getAirlineName(flight);
        const airlineLogoUrl = getAirlineLogoUrl(flight);
        const fallbackBadge = airlineBadge(flight.airline_company);

        return (
          <Paper key={flight.id} className={styles.resultCard} elevation={0}>
            <Box className={styles.logoBox}>
              {airlineLogoUrl ? (
                <Box
                  component="img"
                  src={airlineLogoUrl}
                  alt={`${airlineName} logo`}
                  className={styles.logoImage}
                />
              ) : (
                fallbackBadge
              )}
            </Box>

            <Box className={styles.routeBox}>
              <Typography variant="h6" className={styles.routeTimes}>
                <span className={styles.routeLeg}>
                  {formatLocalTime(flight.departure_time)}{" "}
                  {airportLabel(origin)}
                </span>
                <span className={styles.routeArrow}>→</span>
                <span className={styles.routeLeg}>
                  {formatLocalTime(flight.landing_time)}{" "}
                  {airportLabel(destination)}
                </span>
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                className={styles.routeMeta}
              >
                {airlineName} | {passengers} traveller
                {Number(passengers) > 1 ? "s" : ""} | {cabinClass}
              </Typography>
            </Box>

            <Box className={styles.priceBox}>
              <Typography variant="h6" className={styles.price}>
                EUR {flight.estimated_total_price}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Estimated total
              </Typography>
              <Button
                variant="contained"
                size="small"
                onClick={() =>
                  navigate(`/buy/${flight.id}`, {
                    state: { cabinClass },
                  })
                }
              >
                Buy
              </Button>
            </Box>
          </Paper>
        );
      })}
    </Box>
  );
}
