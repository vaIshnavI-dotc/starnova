import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AlertsProvider } from './context/AlertsContext';
import MainApp from './pages/MainApp';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ProfilePage from './pages/ProfilePage';
import InvestmentsPage from './pages/InvestmentsPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center font-mono text-xs text-ink-muted">
        <span className="text-accent mr-2">◈</span> Loading session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function PublicOnlyRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center font-mono text-xs text-ink-muted">
        <span className="text-accent mr-2">◈</span> Loading session...
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
}

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AlertsProvider>
          <Routes>
            <Route
              path="/login"
              element={
                <PublicOnlyRoute>
                  <LoginPage />
                </PublicOnlyRoute>
              }
            />
            <Route
              path="/signup"
              element={
                <PublicOnlyRoute>
                  <SignupPage />
                </PublicOnlyRoute>
              }
            />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainApp />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/investments"
              element={
                <ProtectedRoute>
                  <InvestmentsPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AlertsProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
