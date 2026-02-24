import { Box, Button, Paper, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

import styles from "./HomeFlightSearchSection.module.css";

const formatLocalTime = (isoString) => {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "--:--";
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

const airlineBadge = (airlineId) => `A${airlineId}`;

export default function HomeFlightResults({ flights, passengers, cabinClass }) {
  const navigate = useNavigate();

  return (
    <Box className={styles.resultsList}>
      {flights.map((flight) => {
        const origin = flight.origin_airport_obj;
        const destination = flight.destination_airport_obj;
        const originCode = origin?.iata_code || origin?.icao_code || "N/A";
        const destinationCode =
          destination?.iata_code || destination?.icao_code || "N/A";

        return (
          <Paper key={flight.id} className={styles.resultCard} elevation={0}>
            <Box className={styles.logoBox}>{airlineBadge(flight.airline_company)}</Box>

            <Box className={styles.routeBox}>
              <Typography variant="h6" className={styles.routeTimes}>
                {formatLocalTime(flight.departure_time)} {originCode} {"->"}{" "}
                {formatLocalTime(flight.landing_time)} {destinationCode}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Airline #{flight.airline_company} | {passengers} traveller
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
                onClick={() => navigate(`/buy/${flight.id}`)}
              >
                Cumpara
              </Button>
            </Box>
          </Paper>
        );
      })}
    </Box>
  );
}
