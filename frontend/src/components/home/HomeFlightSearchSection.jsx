import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";

import HomeFlightResults from "./HomeFlightResults";
import styles from "./HomeFlightSearchSection.module.css";

const formatAirportLabel = (airport) => {
  const code = airport.iata_code || airport.icao_code || "N/A";
  const city = airport.city?.trim() || "Unknown city";
  const country = airport.country_name || "Unknown country";
  return `${code} - ${city}, ${country}`;
};

const formatDateLabel = (dateKey) => {
  const date = new Date(`${dateKey}T12:00:00`);
  if (Number.isNaN(date.getTime())) return dateKey;
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
};

export default function HomeFlightSearchSection({
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
}) {
  return (
    <Container maxWidth="lg" className={styles.container}>
      <Card className={styles.searchCard} elevation={0}>
        <CardContent>
          <Typography variant="h5" className={styles.searchTitle}>
            Search flights
          </Typography>

          <Box className={styles.grid}>
            <Card className={styles.fieldCard} elevation={0}>
              <CardContent>
                <Typography variant="caption" className={styles.label}>
                  From
                </Typography>
                <FormControl fullWidth size="small">
                  <InputLabel id="from-airport-label">From</InputLabel>
                  <Select
                    labelId="from-airport-label"
                    label="From"
                    value={fromAirportId}
                    onChange={(event) => {
                      setFromAirportId(event.target.value);
                      setDepartureDate("");
                    }}
                  >
                    {fromAirportOptions.map((airport) => (
                      <MenuItem key={airport.id} value={String(airport.id)}>
                        {formatAirportLabel(airport)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </CardContent>
            </Card>

            <Card className={styles.fieldCard} elevation={0}>
              <CardContent>
                <Typography variant="caption" className={styles.label}>
                  To
                </Typography>
                <FormControl fullWidth size="small">
                  <InputLabel id="to-airport-label">To</InputLabel>
                  <Select
                    labelId="to-airport-label"
                    label="To"
                    value={toAirportId}
                    onChange={(event) => {
                      setToAirportId(event.target.value);
                      setDepartureDate("");
                    }}
                  >
                    {toAirportOptions.map((airport) => (
                      <MenuItem key={airport.id} value={String(airport.id)}>
                        {formatAirportLabel(airport)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </CardContent>
            </Card>

            <Card className={styles.fieldCard} elevation={0}>
              <CardContent>
                <Typography variant="caption" className={styles.label}>
                  Departure date
                </Typography>
                <FormControl fullWidth size="small" disabled={!toAirportId}>
                  <InputLabel id="departure-date-label">Date</InputLabel>
                  <Select
                    labelId="departure-date-label"
                    label="Date"
                    value={departureDate}
                    onChange={(event) => setDepartureDate(event.target.value)}
                  >
                    {availableDateOptions.map((dateKey) => (
                      <MenuItem key={dateKey} value={dateKey}>
                        {formatDateLabel(dateKey)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </CardContent>
            </Card>

            <Card className={styles.fieldCard} elevation={0}>
              <CardContent className={styles.passengersCard}>
                <Box>
                  <Typography variant="caption" className={styles.label}>
                    Travellers
                  </Typography>
                  <FormControl fullWidth size="small">
                    <InputLabel id="passengers-label">Travellers</InputLabel>
                    <Select
                      labelId="passengers-label"
                      label="Travellers"
                      value={passengers}
                      onChange={(event) => setPassengers(event.target.value)}
                    >
                      {Array.from({ length: 9 }, (_, index) => {
                        const value = String(index + 1);
                        return (
                          <MenuItem key={value} value={value}>
                            {value}
                          </MenuItem>
                        );
                      })}
                    </Select>
                  </FormControl>
                </Box>

                <Box>
                  <Typography variant="caption" className={styles.label}>
                    Cabin class
                  </Typography>
                  <FormControl fullWidth size="small">
                    <InputLabel id="class-label">Class</InputLabel>
                    <Select
                      labelId="class-label"
                      label="Class"
                      value={cabinClass}
                      onChange={(event) => setCabinClass(event.target.value)}
                    >
                      <MenuItem value="economy">Economy</MenuItem>
                      <MenuItem value="business">Business</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              </CardContent>
            </Card>
          </Box>

          <Box className={styles.searchActions}>
            <Button
              variant="contained"
              disabled={!canSearch || isLoadingData}
              onClick={searchFlights}
            >
              Search
            </Button>
          </Box>
        </CardContent>
      </Card>

      {isLoadingData && (
        <Box className={styles.loadingBox}>
          <CircularProgress size={24} />
          <Typography>Loading flights...</Typography>
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {hasSearched && !isLoadingData && results.length === 0 && (
        <Alert severity="info">
          No flights are available for your selection. Try another date or route.
        </Alert>
      )}

      {hasSearched && results.length > 0 && (
        <HomeFlightResults
          flights={results}
          passengers={passengers}
          cabinClass={cabinClass}
        />
      )}
    </Container>
  );
}
