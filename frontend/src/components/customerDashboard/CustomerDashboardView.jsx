import { Alert, Box, Container, Typography } from "@mui/material";

import styles from "./CustomerDashboardView.module.css";
import TicketsPanel from "./TicketsPanel";

export default function CustomerDashboardView({
  user,
  isLoading,
  isCustomer,
  error,
  success,
  ...vm
}) {
  if (isLoading) return <div>Loading...</div>;

  if (!user) {
    return (
      <Container maxWidth="md" className={styles.container}>
        <Typography variant="h5" gutterBottom>
          Customer Dashboard
        </Typography>
        <Alert severity="info">Please log in to view your dashboard.</Alert>
      </Container>
    );
  }

  if (!isCustomer) {
    return (
      <Container maxWidth="md" className={styles.container}>
        <Typography variant="h5" gutterBottom>
          Customer Dashboard
        </Typography>
        <Alert severity="warning">This page is for customers only.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" className={styles.container}>
      <Typography variant="h5" gutterBottom>
        Customer Dashboard
      </Typography>

      {error && (
        <Box className={styles.message}>
          <Alert severity="error">{error}</Alert>
        </Box>
      )}
      {success && (
        <Box className={styles.message}>
          <Alert severity="success">{success}</Alert>
        </Box>
      )}

      <TicketsPanel {...vm} />
    </Container>
  );
}
