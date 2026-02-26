import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import HomePage from "./pages/HomePage";
import CustomerDashboard from "./pages/CustomerDashboard";
import { AuthProvider } from "./context/AuthProvider";
import LoginPage from "./pages/LoginPage";
import AirlineDashboard from "./pages/AirlineDashboard";
import RegisterPage from "./pages/RegisterPage";
import BuyPage from "./pages/BuyPage";
import AdminDashboard from "./pages/AdminDashboard";
import HomeNavbar from "./components/home/HomeNavbar";
import { useAuth } from "./context/AuthContext";
import PaymentProcessingPage from "./pages/PaymentProcessingPage";
import PurchaseSuccessPage from "./pages/PurchaseSuccessPage";
import TicketPage from "./pages/TicketPage";

function AppShell() {
  const { user, logout } = useAuth();

  return (
    <Router>
      <div className="app-container">
        <HomeNavbar user={user} onLogout={logout} />

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/customer/dashboard" element={<CustomerDashboard />} />
          <Route path="/airline/dashboard" element={<AirlineDashboard />} />
          <Route path="/administrator/dashboard" element={<AdminDashboard />} />
          <Route path="/buy/:flightId" element={<BuyPage />} />
          <Route
            path="/buy/:flightId/processing"
            element={<PaymentProcessingPage />}
          />
          <Route path="/buy/:flightId/success" element={<PurchaseSuccessPage />} />
          <Route path="/customer/tickets/:ticketId" element={<TicketPage />} />
        </Routes>
      </div>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}

export default App;
