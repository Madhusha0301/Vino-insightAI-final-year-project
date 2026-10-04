import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';
import Layout from './components/Layout';
import ChatBot from './components/ChatBot';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Predict from './pages/Predict';
import Results from './pages/Results';
import History from './pages/History';
import Trends from './pages/Trends';
import Compare from './pages/Compare';
import AdminPanel from './pages/AdminPanel';
import NotFound from './pages/NotFound';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

function ProtectedRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
}

function AdminRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'admin') return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="predict" element={<Predict />} />
              <Route path="results" element={<Results />} />
              <Route path="history" element={<History />} />
              <Route path="trends" element={<Trends />} />
              <Route path="compare" element={<Compare />} />
              <Route path="admin" element={<AdminRoute><AdminPanel /></AdminRoute>} />
              {/* Unknown page *inside* the dashboard — keeps the sidebar/header
                  so the user stays oriented instead of being thrown out. */}
              <Route path="*" element={<NotFound />} />
            </Route>

            {/* Catch-all for every other unmatched url (project audit fix).
                Without this, React Router matched nothing and rendered an
                entirely blank page — e.g. "/predict", which is an easy and
                very natural guess for the real "/dashboard/predict". */}
            <Route path="*" element={<NotFound />} />
          </Routes>
          <ChatBot />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
