import { Box, Button, Typography } from "@mui/material";

import styles from "./TicketsPanel.module.css";
import TicketsTable from "./TicketsTable";

export default function TicketsPanel({
  tickets,
  isLoadingTickets,
  refreshTickets,
  cancelTicket,
  flightById,
}) {
  return (
    <Box className={styles.root}>
      <Box className={styles.actions}>
        <Button
          type="button"
          variant="outlined"
          onClick={() => refreshTickets()}
          disabled={isLoadingTickets}
        >
          Refresh
        </Button>
      </Box>

      <Box className={styles.header}>
        <Box
          component="img"
          src="/airplane-depart.png"
          alt="Airplane departure"
          className={styles.headerImage}
        />
        <Typography variant="h6" gutterBottom>
          My Tickets
        </Typography>
        <Box
          component="img"
          src="/airplane-arrival.png"
          alt="Airplane arrival"
          className={styles.headerImage}
        />
      </Box>

      <TicketsTable
        tickets={tickets}
        isLoadingTickets={isLoadingTickets}
        onCancel={cancelTicket}
        flightById={flightById}
      />
    </Box>
  );
}
