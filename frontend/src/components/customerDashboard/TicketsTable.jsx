import { Alert, Button, Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

import styles from "./TicketsTable.module.css";

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

export default function TicketsTable({
  tickets,
  isLoadingTickets,
  onCancel,
  flightById,
}) {
  const navigate = useNavigate();

  if (isLoadingTickets) return <Typography>Loading tickets...</Typography>;
  if (!tickets || tickets.length === 0)
    return <Alert severity="info">You have no tickets.</Alert>;

  return (
    <Table size="small" className={styles.table}>
      <TableHead>
        <TableRow>
          <TableCell>ID</TableCell>
          <TableCell>Flight</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Purchased</TableCell>
          <TableCell>Seat</TableCell>
          <TableCell align="right" className={styles.actionCell}>
            Action
          </TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {tickets.map((t) => {
          const f = flightById?.[t.flight];
          const flightLabel = f
            ? `#${f.id} (${formatDateTimeGB(f.departure_time)})`
            : `#${t.flight}`;
          const status = String(t.status ?? "").toLowerCase();
          const isFinalStatus = status === "cancelled" || status === "refunded";

          return (
            <TableRow key={t.id}>
              <TableCell>{t.id}</TableCell>
              <TableCell>{flightLabel}</TableCell>
              <TableCell>{t.status ?? "—"}</TableCell>
              <TableCell>{formatDateTimeGB(t.purchased_at)}</TableCell>
              <TableCell>{t.seat_no ?? "—"}</TableCell>
              <TableCell align="right" className={styles.actionCell}>
                {!isFinalStatus && (
                  <Button
                    size="small"
                    variant="contained"
                    sx={{ mr: 1 }}
                    onClick={() =>
                      navigate(`/customer/tickets/${t.id}`, {
                        state: {
                          ticket: t,
                          flight: f ?? null,
                        },
                      })
                    }
                  >
                    View ticket
                  </Button>
                )}
                <Button
                  size="small"
                  variant="outlined"
                  disabled={isFinalStatus}
                  onClick={() => onCancel(t.id)}
                >
                  Cancel
                </Button>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
