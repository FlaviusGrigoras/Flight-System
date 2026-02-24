import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Tab,
  Tabs,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import { geoService } from "../services/geoService";
import { flightService } from "../services/flightService";
import { ticketService } from "../services/ticketService";
import { useAuth } from "../context/AuthContext";

const formatAirportLabel = (a) => {
  const code = a.iata_code || a.icao_code || "N/A";
  const city = a.city?.trim() ? ` - ${a.city.trim()}` : "";
  return `${code} - ${a.name}${city}`;
};

const toLocalInputValue = (isoString) => {
  if (!isoString) return "";
  const d = new Date(isoString);
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
};

const formatDateTimeGB = (isoString) => {
  if (!isoString) return "";
  const d = new Date(isoString);
  if (Number.isNaN(d.getTime())) return "";
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
};

const getApiErrorMessage = (err, fallback) => {
  return (
    err?.response?.data?.error?.message ||
    err?.response?.data?.detail ||
    err?.response?.data?.error ||
    fallback
  );
};

export default function AirlineDashboard() {
  const { user } = useAuth();

  const [tab, setTab] = useState(0);

  const [countries, setCountries] = useState([]);
  const [isLoadingCountries, setIsLoadingCountries] = useState(true);

  const [originCountryId, setOriginCountryId] = useState("");
  const [originAirports, setOriginAirports] = useState([]);
  const [originAirportId, setOriginAirportId] = useState("");

  const [destinationCountryId, setDestinationCountryId] = useState("");
  const [destinationAirports, setDestinationAirports] = useState([]);
  const [destinationAirportId, setDestinationAirportId] = useState("");

  const [airportQuery, setAirportQuery] = useState("");

  const [departureLocal, setDepartureLocal] = useState("");
  const [landingLocal, setLandingLocal] = useState("");
  const [remainingTickets, setRemainingTickets] = useState(0);

  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [myFlights, setMyFlights] = useState([]);
  const [isLoadingMyFlights, setIsLoadingMyFlights] = useState(false);
  const [selectedFlightId, setSelectedFlightId] = useState("");
  const [editDepartureLocal, setEditDepartureLocal] = useState("");
  const [editLandingLocal, setEditLandingLocal] = useState("");
  const [editRemainingTickets, setEditRemainingTickets] = useState(0);

  const [soldTickets, setSoldTickets] = useState([]);
  const [isLoadingSoldTickets, setIsLoadingSoldTickets] = useState(false);
  const [soldTicketsFlightId, setSoldTicketsFlightId] = useState("");

  const isAirline = user?.role === "airline";

  useEffect(() => {
    let cancelled = false;
    const fetchCountries = async () => {
      setIsLoadingCountries(true);
      try {
        const data = await geoService.getCountries();
        if (!cancelled) setCountries(data);
      } catch {
        if (!cancelled) setError("Failed to load countries.");
      } finally {
        if (!cancelled) setIsLoadingCountries(false);
      }
    };
    fetchCountries();
    return () => {
      cancelled = true;
    };
  }, []);

  const refreshMyFlights = async () => {
    setIsLoadingMyFlights(true);
    try {
      const data = await flightService.getMyFlights();
      setMyFlights(data);
      setError(null);
    } catch (e) {
      setError(getApiErrorMessage(e, "Failed to load my flights."));
    } finally {
      setIsLoadingMyFlights(false);
    }
  };

  const refreshSoldTickets = async () => {
    setIsLoadingSoldTickets(true);
    try {
      const data = await ticketService.getAirlineSoldTickets({
        flightId: soldTicketsFlightId || undefined,
      });
      setSoldTickets(data);
      setError(null);
    } catch (e) {
      setError(getApiErrorMessage(e, "Failed to load sold tickets."));
    } finally {
      setIsLoadingSoldTickets(false);
    }
  };

  useEffect(() => {
    if (!isAirline) return;
    refreshMyFlights();
    refreshSoldTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAirline]);

  useEffect(() => {
    if (!isAirline) return;
    refreshSoldTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [soldTicketsFlightId]);

  useEffect(() => {
    let cancelled = false;
    const fetchOriginAirports = async () => {
      setOriginAirports([]);
      setOriginAirportId("");
      if (!originCountryId) return;
      try {
        const data = await geoService.getAirports({
          countryId: originCountryId,
          q: airportQuery,
          limit: 500,
        });
        if (!cancelled) setOriginAirports(data);
      } catch {
        if (!cancelled) setError("Failed to load origin airports.");
      }
    };
    fetchOriginAirports();
    return () => {
      cancelled = true;
    };
  }, [originCountryId, airportQuery]);

  useEffect(() => {
    let cancelled = false;
    const fetchDestinationAirports = async () => {
      setDestinationAirports([]);
      setDestinationAirportId("");
      if (!destinationCountryId) return;
      try {
        const data = await geoService.getAirports({
          countryId: destinationCountryId,
          q: airportQuery,
          limit: 500,
        });
        if (!cancelled) setDestinationAirports(data);
      } catch {
        if (!cancelled) setError("Failed to load destination airports.");
      }
    };
    fetchDestinationAirports();
    return () => {
      cancelled = true;
    };
  }, [destinationCountryId, airportQuery]);

  const canSubmit = useMemo(() => {
    return (
      isAirline &&
      originAirportId &&
      destinationAirportId &&
      departureLocal &&
      landingLocal &&
      Number.isFinite(Number(remainingTickets))
    );
  }, [
    isAirline,
    originAirportId,
    destinationAirportId,
    departureLocal,
    landingLocal,
    remainingTickets,
    ]);

  const handleCreateFlight = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      const payload = {
        origin_airport: Number(originAirportId),
        destination_airport: Number(destinationAirportId),
        departure_time: new Date(departureLocal).toISOString(),
        landing_time: new Date(landingLocal).toISOString(),
        remaining_tickets: Number(remainingTickets),
      };
      await flightService.createFlight(payload);
      setSuccess("Flight created.");
      await refreshMyFlights();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to create flight."));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectFlightForEdit = (flightId) => {
    setSelectedFlightId(String(flightId));
    const f = myFlights.find((x) => String(x.id) === String(flightId));
    if (!f) return;
    setEditDepartureLocal(toLocalInputValue(f.departure_time));
    setEditLandingLocal(toLocalInputValue(f.landing_time));
    setEditRemainingTickets(f.remaining_tickets ?? 0);
  };

  const handleUpdateFlight = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    if (!selectedFlightId) return;

    try {
      const payload = {
        departure_time: new Date(editDepartureLocal).toISOString(),
        landing_time: new Date(editLandingLocal).toISOString(),
        remaining_tickets: Number(editRemainingTickets),
      };
      await flightService.updateMyFlight(selectedFlightId, payload);
      setSuccess("Flight updated.");
      await refreshMyFlights();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to update flight."));
    }
  };

  const handleDeleteFlight = async (flightId) => {
    setError(null);
    setSuccess(null);
    try {
      await flightService.deleteMyFlight(flightId);
      setSuccess("Flight deleted.");
      if (String(selectedFlightId) === String(flightId)) setSelectedFlightId("");
      await refreshMyFlights();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to delete flight."));
    }
  };

  if (!isAirline) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ mt: 4 }}>
          <Alert severity="warning">
            This page is available only for airline users.
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Airline dashboard
        </Typography>

        {(error || success) && (
          <Alert severity={error ? "error" : "success"} sx={{ mb: 2 }}>
            {error || success}
          </Alert>
        )}

        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
          <Tab label="Create flight" />
          <Tab label="Manage flights" />
          <Tab label="Tickets sold" />
        </Tabs>

        {tab === 0 && (
          <Box component="form" onSubmit={handleCreateFlight}>
            <Typography variant="h6" sx={{ mb: 1 }}>
              Create flight
            </Typography>

            <TextField
              label="Filter airports"
              value={airportQuery}
              onChange={(e) => setAirportQuery(e.target.value)}
              fullWidth
              sx={{ mb: 2 }}
              placeholder="Search by name, city, IATA/ICAO"
            />

            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 2,
                mb: 2,
              }}
            >
              <FormControl fullWidth disabled={isLoadingCountries}>
                <InputLabel id="origin-country-label">Origin country</InputLabel>
                <Select
                  labelId="origin-country-label"
                  label="Origin country"
                  value={originCountryId}
                  onChange={(e) => setOriginCountryId(e.target.value)}
                >
                  {countries.map((c) => (
                    <MenuItem key={c.id} value={String(c.id)}>
                      {c.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth disabled={!originCountryId}>
                <InputLabel id="origin-airport-label">Origin airport</InputLabel>
                <Select
                  labelId="origin-airport-label"
                  label="Origin airport"
                  value={originAirportId}
                  onChange={(e) => setOriginAirportId(e.target.value)}
                >
                  {originAirports.map((a) => (
                    <MenuItem key={a.id} value={String(a.id)}>
                      {formatAirportLabel(a)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth disabled={isLoadingCountries}>
                <InputLabel id="dest-country-label">
                  Destination country
                </InputLabel>
                <Select
                  labelId="dest-country-label"
                  label="Destination country"
                  value={destinationCountryId}
                  onChange={(e) => setDestinationCountryId(e.target.value)}
                >
                  {countries.map((c) => (
                    <MenuItem key={c.id} value={String(c.id)}>
                      {c.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth disabled={!destinationCountryId}>
                <InputLabel id="dest-airport-label">
                  Destination airport
                </InputLabel>
                <Select
                  labelId="dest-airport-label"
                  label="Destination airport"
                  value={destinationAirportId}
                  onChange={(e) => setDestinationAirportId(e.target.value)}
                >
                  {destinationAirports.map((a) => (
                    <MenuItem key={a.id} value={String(a.id)}>
                      {formatAirportLabel(a)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr",
                gap: 2,
                mb: 2,
              }}
            >
              <TextField
                label="Departure time"
                type="datetime-local"
                value={departureLocal}
                onChange={(e) => setDepartureLocal(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
                required
              />
              <TextField
                label="Landing time"
                type="datetime-local"
                value={landingLocal}
                onChange={(e) => setLandingLocal(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
                required
              />
              <TextField
                label="Remaining tickets"
                type="number"
                value={remainingTickets}
                onChange={(e) => setRemainingTickets(e.target.value)}
                fullWidth
                required
                inputProps={{ min: 0 }}
              />
            </Box>

            <Button
              type="submit"
              variant="contained"
              disabled={!canSubmit || isSubmitting}
            >
              Create flight
            </Button>
          </Box>
        )}

        {tab === 1 && (
          <Box>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
              <Typography variant="h6">Manage flights</Typography>
              <Button
                type="button"
                variant="outlined"
                onClick={refreshMyFlights}
                disabled={isLoadingMyFlights}
              >
                Refresh
              </Button>
            </Box>

            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Origin</TableCell>
                  <TableCell>Destination</TableCell>
                  <TableCell>Departure</TableCell>
                  <TableCell>Landing</TableCell>
                  <TableCell>Remaining</TableCell>
                  <TableCell />
                </TableRow>
              </TableHead>
              <TableBody>
                {myFlights.map((f) => (
                  <TableRow
                    key={f.id}
                    hover
                    selected={String(selectedFlightId) === String(f.id)}
                    onClick={() => handleSelectFlightForEdit(f.id)}
                    sx={{ cursor: "pointer" }}
                  >
                    <TableCell>{f.id}</TableCell>
                    <TableCell>
                      {formatAirportLabel(f.origin_airport)}
                    </TableCell>
                    <TableCell>
                      {formatAirportLabel(f.destination_airport)}
                    </TableCell>
                    <TableCell>
                      {formatDateTimeGB(f.departure_time)}
                    </TableCell>
                    <TableCell>
                      {formatDateTimeGB(f.landing_time)}
                    </TableCell>
                    <TableCell>{f.remaining_tickets}</TableCell>
                    <TableCell>
                      <Button
                        type="button"
                        color="error"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteFlight(f.id);
                        }}
                      >
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                Edit flight
              </Typography>
              {!selectedFlightId ? (
                <Typography variant="body2">
                  Select a flight from the table to edit it.
                </Typography>
              ) : (
                <Box component="form" onSubmit={handleUpdateFlight}>
                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr 1fr",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <TextField
                      label="Departure time"
                      type="datetime-local"
                      value={editDepartureLocal}
                      onChange={(e) => setEditDepartureLocal(e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      fullWidth
                      required
                    />
                    <TextField
                      label="Landing time"
                      type="datetime-local"
                      value={editLandingLocal}
                      onChange={(e) => setEditLandingLocal(e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      fullWidth
                      required
                    />
                    <TextField
                      label="Remaining tickets"
                      type="number"
                      value={editRemainingTickets}
                      onChange={(e) => setEditRemainingTickets(e.target.value)}
                      fullWidth
                      required
                      inputProps={{ min: 0 }}
                    />
                  </Box>

                  <Button type="submit" variant="contained">
                    Save changes
                  </Button>
                </Box>
              )}
            </Box>
          </Box>
        )}

        {tab === 2 && (
          <Box>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center", mb: 2 }}>
              <Typography variant="h6">Tickets sold</Typography>
              <FormControl sx={{ minWidth: 220 }}>
                <InputLabel id="sold-flight-label">Flight</InputLabel>
                <Select
                  labelId="sold-flight-label"
                  label="Flight"
                  value={soldTicketsFlightId}
                  onChange={(e) => setSoldTicketsFlightId(e.target.value)}
                >
                  <MenuItem value="">All flights</MenuItem>
                  {myFlights.map((f) => (
                    <MenuItem key={f.id} value={String(f.id)}>
                      #{f.id} {formatAirportLabel(f.origin_airport)} →{" "}
                      {formatAirportLabel(f.destination_airport)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                type="button"
                variant="outlined"
                onClick={refreshSoldTickets}
                disabled={isLoadingSoldTickets}
              >
                Refresh
              </Button>
            </Box>

            <Typography variant="body2" sx={{ mb: 1 }}>
              Total: {soldTickets.length}
            </Typography>

            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Ticket ID</TableCell>
                  <TableCell>Flight</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Purchased</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {soldTickets.map((t) => (
                  <TableRow key={t.id}>
                    <TableCell>{t.id}</TableCell>
                    <TableCell>
                      #{t.flight?.id}{" "}
                      {t.flight?.origin_airport
                        ? formatAirportLabel(t.flight.origin_airport)
                        : ""}
                      {" → "}
                      {t.flight?.destination_airport
                        ? formatAirportLabel(t.flight.destination_airport)
                        : ""}
                    </TableCell>
                    <TableCell>
                      {t.customer?.first_name} {t.customer?.last_name} (
                      {t.customer?.email})
                    </TableCell>
                    <TableCell>{t.status}</TableCell>
                    <TableCell>
                      {t.purchased_at
                        ? formatDateTimeGB(t.purchased_at)
                        : ""}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        )}
      </Box>
    </Container>
  );
}
