import { useEffect, useState } from "react";

import apiClient from "../services/apiClient";
import { AuthContext } from "./AuthContext";

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("token");

      if (token) {
        try {
          const response = await apiClient.get("/accounts/me/");
          setUser(response.data);
        } catch (error) {
          console.error("Error validating token: ", error);
          localStorage.removeItem("token");
          localStorage.removeItem("refreshToken");
        }
      }

      setIsLoading(false);
    };

    fetchUser();
  }, []);

  const login = (userData, token) => {
    localStorage.setItem("token", token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
