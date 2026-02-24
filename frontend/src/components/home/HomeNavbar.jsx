import { AppBar, Box, Button, Menu, MenuItem, Toolbar, Typography } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import styles from "./HomeNavbar.module.css";

const resolveMenuItemsByRole = (role) => {
  if (role === "customer") {
    return [{ label: "Customer Dashboard", action: "navigate", path: "/customer/dashboard" }];
  }
  if (role === "airline") {
    return [{ label: "Airline Dashboard", action: "navigate", path: "/airline/dashboard" }];
  }
  if (role === "administrator") {
    return [{ label: "Admin Panel", action: "disabled" }];
  }
  return [];
};

export default function HomeNavbar({ user, onLogout }) {
  const navigate = useNavigate();
  const [menuAnchor, setMenuAnchor] = useState(null);

  const openMenu = (event) => {
    setMenuAnchor(event.currentTarget);
  };

  const closeMenu = () => {
    setMenuAnchor(null);
  };

  const items = resolveMenuItemsByRole(user?.role);
  const displayName = user?.username ?? "User";

  return (
    <AppBar position="sticky" className={styles.bar}>
      <Toolbar className={styles.toolbar}>
        <Typography variant="h6" className={styles.title} onClick={() => navigate("/")}>
          Find flights
        </Typography>

        {!user ? (
          <Box className={styles.actions}>
            <Button variant="outlined" onClick={() => navigate("/login")}>
              Login
            </Button>
            <Button variant="contained" onClick={() => navigate("/register")}>
              Register
            </Button>
          </Box>
        ) : (
          <Box className={styles.actions}>
            <Button variant="outlined" onClick={openMenu}>
              {displayName} Menu
            </Button>
            <Menu
              anchorEl={menuAnchor}
              open={Boolean(menuAnchor)}
              onClose={closeMenu}
            >
              {items.map((item) => (
                <MenuItem
                  key={item.label}
                  disabled={item.action === "disabled"}
                  onClick={() => {
                    closeMenu();
                    if (item.action === "navigate" && item.path) navigate(item.path);
                  }}
                >
                  {item.label}
                </MenuItem>
              ))}
              <MenuItem
                onClick={() => {
                  closeMenu();
                  onLogout();
                  navigate("/");
                }}
              >
                Logout
              </MenuItem>
            </Menu>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
