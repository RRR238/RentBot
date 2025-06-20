import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginForm from "./components/LoginForm";
import OffersPage from "./components/OffersPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginForm />} />
        <Route path="/offers" element={<OffersPage />} />
        {/* Placeholder for AI Search page */}
        <Route path="/ai-search" element={<div style={{padding: "2rem"}}><h1>AI Search (Coming Soon)</h1></div>} />
      </Routes>
    </Router>
  );
}

export default App;