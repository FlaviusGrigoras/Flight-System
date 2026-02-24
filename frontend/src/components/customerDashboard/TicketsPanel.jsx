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

      <Typography variant="h6" gutterBottom>
        My Tickets
      </Typography>

      <TicketsTable
        tickets={tickets}
        isLoadingTickets={isLoadingTickets}
        onCancel={cancelTicket}
        flightById={flightById}
      />
    </Box>
  );
}

