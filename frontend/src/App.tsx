import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./components/AuthContext.tsx"; // Assuming you have an auth context setup
import Auth from "./components/Auth.tsx";
import History from "./components/History.tsx";
import Dashboard from "./components/Dashboard.tsx";
import Navbar1 from "./components/Navbar.tsx";
import ServiceRequest from "./components/ServiceRequest.tsx";
import Services from "./components/Services.tsx";
import "./App.css";

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Navbar1 />
      <Router>
        <Routes>
          <Route path="/auth" element={<Auth />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
            <Route path="/servicerequest" element={<ServiceRequest />} />
            <Route path="/services" element={<Services />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
