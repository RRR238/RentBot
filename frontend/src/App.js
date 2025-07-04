import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import OffersPage from "./components/OffersPage";
import AISearchPage from "./components/AISearchPage";
import LoginForm from "./components/LoginForm";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/offers" element={<OffersPage />} />
        <Route path="/ai-search" element={<AISearchPage />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;