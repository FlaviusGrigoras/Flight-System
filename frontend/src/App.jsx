import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import HomePage from "./pages/HomePage";
import CustomerDashboard from "./pages/CustomerDashboard";
import { AuthProvider } from "./context/AuthProvider";
import LoginPage from "./pages/LoginPage";
import AirlineDashboard from "./pages/AirlineDashboard";
import RegisterPage from "./pages/RegisterPage";
import BuyPage from "./pages/BuyPage";
import AdminDashboard from "./pages/AdminDashboard";

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          {/* Navbar */}

          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/customer/dashboard" element={<CustomerDashboard />} />
            <Route path="/airline/dashboard" element={<AirlineDashboard />} />
            <Route path="/administrator/dashboard" element={<AdminDashboard />} />
            <Route path="/buy/:flightId" element={<BuyPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
