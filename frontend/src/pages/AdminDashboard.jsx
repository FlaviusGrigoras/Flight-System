import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";

import { useAuth } from "../context/AuthContext";
import { adminService } from "../services/adminService";
import { geoService } from "../services/geoService";
import { ticketService } from "../services/ticketService";

const getApiErrorMessage = (err, fallback) => {
  const detail = err?.response?.data?.detail;
  if (detail) return detail;

  const errorMessage = err?.response?.data?.error?.message || err?.response?.data?.error;
  if (errorMessage) return errorMessage;

  const fieldErrors = err?.response?.data;
  if (fieldErrors && typeof fieldErrors === "object" && !Array.isArray(fieldErrors)) {
    const [firstField] = Object.keys(fieldErrors);
    const firstValue = fieldErrors[firstField];
    if (Array.isArray(firstValue) && firstValue.length > 0) {
      return `${firstField}: ${firstValue[0]}`;
    }
  }

  return fallback;
};

const getUserLabel = (user) => {
  if (!user) return "-";
  if (user.email) return `${user.username} (${user.email})`;
  return user.username || "-";
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

const isTicketActive = (ticket) =>
  String(ticket?.status ?? "").toUpperCase() === "ACTIVE";

export default function AdminDashboard() {
  const { user, isLoading } = useAuth();
  const isAdministrator = user?.role === "administrator";

  const [customers, setCustomers] = useState([]);
  const [airlines, setAirlines] = useState([]);
  const [administrators, setAdministrators] = useState([]);
  const [countries, setCountries] = useState([]);

  const [isLoadingCustomers, setIsLoadingCustomers] = useState(false);
  const [isLoadingAirlines, setIsLoadingAirlines] = useState(false);
  const [isLoadingAdministrators, setIsLoadingAdministrators] = useState(false);
  const [isLoadingCountries, setIsLoadingCountries] = useState(false);
  const [isSubmittingAdmin, setIsSubmittingAdmin] = useState(false);
  const [isSubmittingAirline, setIsSubmittingAirline] = useState(false);
  const [isLoadingTickets, setIsLoadingTickets] = useState(false);
  const [isRefundingTicketId, setIsRefundingTicketId] = useState(null);

  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const [adminEmail, setAdminEmail] = useState("");
  const [adminUsername, setAdminUsername] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [adminFirstName, setAdminFirstName] = useState("");
  const [adminLastName, setAdminLastName] = useState("");
  const [airlineName, setAirlineName] = useState("");
  const [airlineCountryId, setAirlineCountryId] = useState("");
  const [airlineEmail, setAirlineEmail] = useState("");
  const [airlineUsername, setAirlineUsername] = useState("");
  const [airlinePassword, setAirlinePassword] = useState("");
  const [tickets, setTickets] = useState([]);

  const clearMessages = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  const loadCustomers = useCallback(async () => {
    setIsLoadingCustomers(true);
    try {
      const data = await adminService.getCustomers();
      setCustomers(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load customers."));
    } finally {
      setIsLoadingCustomers(false);
    }
  }, []);

  const loadAirlines = useCallback(async () => {
    setIsLoadingAirlines(true);
    try {
      const data = await adminService.getAirlines();
      setAirlines(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load airlines."));
    } finally {
      setIsLoadingAirlines(false);
    }
  }, []);

  const loadAdministrators = useCallback(async () => {
    setIsLoadingAdministrators(true);
    try {
      const data = await adminService.getAdministrators();
      setAdministrators(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load administrators."));
    } finally {
      setIsLoadingAdministrators(false);
    }
  }, []);

  const loadCountries = useCallback(async () => {
    setIsLoadingCountries(true);
    try {
      const data = await geoService.getCountries();
      setCountries(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load countries."));
    } finally {
      setIsLoadingCountries(false);
    }
  }, []);

  const loadTickets = useCallback(async () => {
    setIsLoadingTickets(true);
    try {
      const data = await ticketService.getAdminTickets();
      setTickets(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load tickets."));
    } finally {
      setIsLoadingTickets(false);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    clearMessages();
    await Promise.all([
      loadCustomers(),
      loadAirlines(),
      loadAdministrators(),
      loadCountries(),
      loadTickets(),
    ]);
  }, [
    clearMessages,
    loadAdministrators,
    loadAirlines,
    loadCountries,
    loadCustomers,
    loadTickets,
  ]);

  useEffect(() => {
    if (!isAdministrator) return;
    refreshAll();
  }, [isAdministrator, refreshAll]);

  const removeCustomer = async (customerId) => {
    clearMessages();
    try {
      await adminService.deleteCustomer(customerId);
      setSuccess(`Customer #${customerId} removed.`);
      setCustomers((prev) => prev.filter((customer) => customer.id !== customerId));
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to remove customer."));
    }
  };

  const removeAirline = async (airlineId) => {
    clearMessages();
    try {
      await adminService.deleteAirline(airlineId);
      setSuccess(`Airline #${airlineId} removed.`);
      setAirlines((prev) => prev.filter((airline) => airline.id !== airlineId));
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to remove airline."));
    }
  };

  const removeAdministrator = async (administratorId) => {
    clearMessages();
    try {
      await adminService.deleteAdministrator(administratorId);
      setSuccess(`Administrator #${administratorId} removed.`);
      setAdministrators((prev) =>
        prev.filter((administrator) => administrator.id !== administratorId)
      );
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to remove administrator."));
    }
  };

  const refundTicket = async (ticketId) => {
    clearMessages();
    setIsRefundingTicketId(ticketId);
    try {
      const updated = await ticketService.refundTicket(ticketId);
      setSuccess(`Ticket #${ticketId} refunded.`);
      setTickets((prev) =>
        prev.map((ticket) => (ticket.id === ticketId ? updated : ticket))
      );
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to refund ticket."));
    } finally {
      setIsRefundingTicketId(null);
    }
  };

  const createAdministrator = async (event) => {
    event.preventDefault();
    clearMessages();
    setIsSubmittingAdmin(true);

    const payload = {
      email: adminEmail,
      password: adminPassword,
      first_name: adminFirstName,
      last_name: adminLastName,
    };
    if (adminUsername.trim()) payload.username = adminUsername.trim();

    try {
      await adminService.createAdministrator(payload);
      setSuccess("Administrator created successfully.");
      setAdminEmail("");
      setAdminUsername("");
      setAdminPassword("");
      setAdminFirstName("");
      setAdminLastName("");
      await loadAdministrators();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to create administrator."));
    } finally {
      setIsSubmittingAdmin(false);
    }
  };

  const createAirline = async (event) => {
    event.preventDefault();
    clearMessages();
    setIsSubmittingAirline(true);

    const payload = {
      name: airlineName,
      country_id: Number(airlineCountryId),
      username: airlineUsername,
      email: airlineEmail,
      password: airlinePassword,
    };

    try {
      await adminService.createAirline(payload);
      setSuccess("Airline created successfully.");
      setAirlineName("");
      setAirlineCountryId("");
      setAirlineUsername("");
      setAirlineEmail("");
      setAirlinePassword("");
      await loadAirlines();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to create airline."));
    } finally {
      setIsSubmittingAirline(false);
    }
  };

  if (isLoading) return <div>Loading...</div>;

  if (!user) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h5" gutterBottom>
          Admin Dashboard
        </Typography>
        <Alert severity="info">Please log in to view the admin dashboard.</Alert>
      </Container>
    );
  }

  if (!isAdministrator) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h5" gutterBottom>
          Admin Dashboard
        </Typography>
        <Alert severity="warning">This page is for administrators only.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 2,
          gap: 2,
          flexWrap: "wrap",
        }}
      >
        <Typography variant="h5">Admin Dashboard</Typography>
        <Button variant="outlined" onClick={refreshAll}>
          Refresh all
        </Button>
      </Box>

      {error && (
        <Box sx={{ mb: 2 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      )}

      {success && (
        <Box sx={{ mb: 2 }}>
          <Alert severity="success">{success}</Alert>
        </Box>
      )}

      <Paper sx={{ p: 2, mb: 3 }} elevation={2}>
        <Typography variant="h6" gutterBottom>
          Create Administrator
        </Typography>

        <Box
          component="form"
          onSubmit={createAdministrator}
          sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 2 }}
        >
          <TextField
            label="First name"
            value={adminFirstName}
            onChange={(event) => setAdminFirstName(event.target.value)}
            required
          />
          <TextField
            label="Last name"
            value={adminLastName}
            onChange={(event) => setAdminLastName(event.target.value)}
            required
          />
          <TextField
            label="Email"
            type="email"
            value={adminEmail}
            onChange={(event) => setAdminEmail(event.target.value)}
            required
          />
          <TextField
            label="Username (optional)"
            value={adminUsername}
            onChange={(event) => setAdminUsername(event.target.value)}
          />
          <TextField
            label="Password"
            type="password"
            value={adminPassword}
            onChange={(event) => setAdminPassword(event.target.value)}
            required
          />
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Button type="submit" variant="contained" disabled={isSubmittingAdmin}>
              {isSubmittingAdmin ? "Creating..." : "Create"}
            </Button>
          </Box>
        </Box>
      </Paper>

      <Paper sx={{ p: 2, mb: 3 }} elevation={2}>
        <Typography variant="h6" gutterBottom>
          Create Airline
        </Typography>

        <Box
          component="form"
          onSubmit={createAirline}
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: 2,
          }}
        >
          <TextField
            label="Airline name"
            value={airlineName}
            onChange={(event) => setAirlineName(event.target.value)}
            required
          />
          <FormControl required>
            <InputLabel id="admin-airline-country-label">Country</InputLabel>
            <Select
              labelId="admin-airline-country-label"
              label="Country"
              value={airlineCountryId}
              onChange={(event) => setAirlineCountryId(event.target.value)}
              disabled={isLoadingCountries}
            >
              {countries.map((country) => (
                <MenuItem key={country.id} value={String(country.id)}>
                  {country.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Username"
            value={airlineUsername}
            onChange={(event) => setAirlineUsername(event.target.value)}
            required
          />
          <TextField
            label="Email"
            type="email"
            value={airlineEmail}
            onChange={(event) => setAirlineEmail(event.target.value)}
            required
          />
          <TextField
            label="Password"
            type="password"
            value={airlinePassword}
            onChange={(event) => setAirlinePassword(event.target.value)}
            required
          />
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Button type="submit" variant="contained" disabled={isSubmittingAirline}>
              {isSubmittingAirline ? "Creating..." : "Create"}
            </Button>
          </Box>
        </Box>
      </Paper>

      <Paper sx={{ p: 2, mb: 3 }} elevation={2}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 1,
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          <Typography variant="h6">Customers</Typography>
          <Button variant="text" onClick={loadCustomers} disabled={isLoadingCustomers}>
            {isLoadingCustomers ? "Loading..." : "Refresh"}
          </Button>
        </Box>

        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>User</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4}>No customers found.</TableCell>
              </TableRow>
            ) : (
              customers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell>{customer.id}</TableCell>
                  <TableCell>{`${customer.first_name} ${customer.last_name}`}</TableCell>
                  <TableCell>{getUserLabel(customer.user)}</TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      color="error"
                      onClick={() => removeCustomer(customer.id)}
                    >
                      Remove
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Paper>

      <Paper sx={{ p: 2, mb: 3 }} elevation={2}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 1,
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          <Typography variant="h6">Airlines</Typography>
          <Button variant="text" onClick={loadAirlines} disabled={isLoadingAirlines}>
            {isLoadingAirlines ? "Loading..." : "Refresh"}
          </Button>
        </Box>

        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Country</TableCell>
              <TableCell>User</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {airlines.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5}>No airlines found.</TableCell>
              </TableRow>
            ) : (
              airlines.map((airline) => (
                <TableRow key={airline.id}>
                  <TableCell>{airline.id}</TableCell>
                  <TableCell>{airline.name}</TableCell>
                  <TableCell>{airline.country_name || "-"}</TableCell>
                  <TableCell>{getUserLabel(airline.user)}</TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      color="error"
                      onClick={() => removeAirline(airline.id)}
                    >
                      Remove
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Paper>

      <Paper sx={{ p: 2, mb: 3 }} elevation={2}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 1,
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          <Typography variant="h6">Administrators</Typography>
          <Button
            variant="text"
            onClick={loadAdministrators}
            disabled={isLoadingAdministrators}
          >
            {isLoadingAdministrators ? "Loading..." : "Refresh"}
          </Button>
        </Box>

        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>User</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {administrators.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4}>No administrators found.</TableCell>
              </TableRow>
            ) : (
              administrators.map((administrator) => {
                const isCurrentUser = administrator?.user?.id === user.id;
                return (
                  <TableRow key={administrator.id}>
                    <TableCell>{administrator.id}</TableCell>
                    <TableCell>{`${administrator.first_name} ${administrator.last_name}`}</TableCell>
                    <TableCell>{getUserLabel(administrator.user)}</TableCell>
                    <TableCell align="right">
                      <Button
                        size="small"
                        color="error"
                        disabled={isCurrentUser}
                        onClick={() => removeAdministrator(administrator.id)}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </Paper>

      <Paper sx={{ p: 2 }} elevation={2}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 1,
            gap: 2,
            flexWrap: "wrap",
          }}
        >
          <Typography variant="h6">Purchased Tickets</Typography>
          <Button variant="text" onClick={loadTickets} disabled={isLoadingTickets}>
            {isLoadingTickets ? "Loading..." : "Refresh"}
          </Button>
        </Box>

        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Flight</TableCell>
              <TableCell>Airline</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Purchased</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7}>No tickets found.</TableCell>
              </TableRow>
            ) : (
              tickets.map((ticket) => (
                <TableRow key={ticket.id}>
                  <TableCell>{ticket.id}</TableCell>
                  <TableCell>{ticket.flight?.id ? `#${ticket.flight.id}` : "-"}</TableCell>
                  <TableCell>{ticket.flight?.airline_company?.name || "-"}</TableCell>
                  <TableCell>
                    {ticket.customer?.first_name} {ticket.customer?.last_name}
                  </TableCell>
                  <TableCell>{ticket.status}</TableCell>
                  <TableCell>{formatDateTimeGB(ticket.purchased_at)}</TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      variant="outlined"
                      disabled={
                        !isTicketActive(ticket) || isRefundingTicketId === ticket.id
                      }
                      onClick={() => refundTicket(ticket.id)}
                    >
                      {isRefundingTicketId === ticket.id ? "Refunding..." : "Refund"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Paper>
    </Container>
  );
}
