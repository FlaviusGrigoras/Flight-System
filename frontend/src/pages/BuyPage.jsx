import { Alert, Button, Container, Typography } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";

export default function BuyPage() {
  const { flightId } = useParams();
  const navigate = useNavigate();

  return (
    <Container maxWidth="md" sx={{ py: 5 }}>
      <Typography variant="h4" gutterBottom>
        Buy Flight
      </Typography>
      <Typography variant="body1" gutterBottom>
        Flight selected: #{flightId}
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Purchase page will be implemented next.
      </Alert>
      <Button variant="outlined" onClick={() => navigate("/")}>
        Back to search
      </Button>
    </Container>
  );
}

