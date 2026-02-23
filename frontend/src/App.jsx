import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import HomePage from "./pages/HomePage";
import CustomerDashboard from "./pages/CustomerDashboard";
import { AuthProvider } from "./context/AuthProvider";
import LoginPage from "./pages/LoginPage";

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          {/* Navbar */}

          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/customer/dashboard" element={<CustomerDashboard />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
