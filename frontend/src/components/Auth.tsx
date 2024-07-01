import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import '../styles/Auth.css'

const Auth: React.FC = () => {
  const [username, setUsername] = useState<string>(""); // Explicitly define state type as string
  const [password, setPassword] = useState<string>(""); // Explicitly define state type as string
  const [isSigningIn, setIsSigningIn] = useState<boolean>(true); // State to toggle between sign in and sign up, explicitly typed as boolean
  const navigate = useNavigate(); // Hook from React Router v6 for redirection

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/dashboard"); // Change '/dashboard' to the appropriate route
    }
  },[navigate]); // Dependency array includes navigate to ensure effect is run when navigate changes

  const handleLogin = async (
    event: React.FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/authe/login/", {
        username,
        password,
      });
      localStorage.setItem("access_token", response.data.access);
      navigate("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const handleSignUp = async (
    event: React.FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/authe/signup/", {
        username,
        password,
      });
      localStorage.setItem("access_token", response.data.access);
      navigate("/dashboard");
    } catch (error) {
      console.error("Signup failed:", error);
    }
  };

  const toggleMode = () => {
    setIsSigningIn(!isSigningIn);
  };

  return (
    <div className="auth-container">
      <div className="auth-form">
        <form onSubmit={isSigningIn ? handleLogin : handleSignUp}>
          <div className="form-group">
            <label>
              Username:
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </label>
          </div>
          <div className="form-group">
            <label>
              Password:
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
          </div>

          <button type="submit">{isSigningIn ? "Sign In" : "Sign Up"}</button>
        </form>
        <button onClick={toggleMode}>
          Switch to {isSigningIn ? "Sign Up" : "Sign In"}
        </button>
      </div>
    </div>
  );
};

export default Auth;
