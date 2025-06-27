import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
       const response = await fetch("http://localhost:5000/login", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ username, password }),
       });
      if (response.ok) {
        const data = await response.json();
        if (data.token && data.type === "bearer") {
          // Store token if needed
          localStorage.setItem("jwtToken", data.token);
          localStorage.setItem("jwtTokenExpiry", (Date.now() + 60 * 60 * 1000).toString());
          // Navigate to Offers page
          navigate("/offers");
        } else {
          setMessage("Invalid response from server.");
        }
      } else {
        setMessage("Login failed.");
      }
    } catch (error) {
      setMessage("Error connecting to server.");
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      {message && <p style={{textAlign: "center"}}>{message}</p>}
    </div>
  );
}

export default LoginForm;