import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import HomePage from "./pages/HomePage";
import CustomerDashboard from "./pages/CustomerDashboard";

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* Navbar */}

        <Routes>
          <Route path="/" element={<HomePage />} />

          <Route path="/customer/dashboard" element={<CustomerDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
