import { useState } from "react";

import {
  Alert,
  Button,
  TextField,
  Box,
  Typography,
  Container,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import apiClient from "../services/apiClient";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await apiClient.post("/accounts/login/", {
        username,
        password,
      });
      const { access, refresh } = response.data.tokens;
      const user = response.data.user;

      localStorage.setItem("refreshToken", refresh);
      login(user, access);

      navigate("/");
    } catch (err) {
      const errorMessage =
        err.response?.data?.error?.message ||
        "Error login. Verify your credentials and try again";
      setError(errorMessage);
    }
  };

  return (
    <Container maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Typography component="h1" variant="h5">
          Login
        </Typography>
        <Box component="form" onSubmit={handleLogin} sx={{ mt: 1 }}>
          {error && (
            <Alert severity="error" sx={{ width: "100%", mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            margin="normal"
            required
            fullWidth
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Login
          </Button>
        </Box>
      </Box>
    </Container>
  );
}
