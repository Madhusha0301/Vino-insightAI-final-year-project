import React, { createContext, useContext, useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:5000/api';
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('vino_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('vino_token') || null);

  const persist = (userData, authToken) => {
    localStorage.setItem('vino_user', JSON.stringify(userData));
    localStorage.setItem('vino_token', authToken);
    setUser(userData);
    setToken(authToken);
  };

  const login = async (email, password) => {
    try {
      const res = await axios.post(`${API_BASE}/login`, { email, password });
      persist(res.data.user, res.data.token);
      return { success: true, user: res.data.user };
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Login failed. Is the backend running?' };
    }
  };

  const signup = async ({ name, email, password, role, company_name }) => {
    try {
      const res = await axios.post(`${API_BASE}/signup`, { name, email, password, role, company_name });
      return { success: true, user: res.data.user, message: res.data.message };
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Signup failed. Is the backend running?' };
    }
  };

  const logout = () => {
    localStorage.removeItem('vino_user');
    localStorage.removeItem('vino_token');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
export { API_BASE };
