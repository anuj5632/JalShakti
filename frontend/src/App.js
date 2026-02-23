import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Pages
import LoginPage from './pages/LoginPage';
import HomeSetupPage from './pages/HomeSetupPage';
import Dashboard from './pages/Dashboard';
import SourcesPage from './pages/SourcesPage';
import AlertsPage from './pages/AlertsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import SettingsPage from './pages/SettingsPage';

// Components
import Sidebar from './components/Sidebar';
import LoadingScreen from './components/LoadingScreen';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, homeSetupComplete } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!homeSetupComplete && window.location.pathname !== '/setup') {
    return <Navigate to="/setup" replace />;
  }

  return children;
};

// Layout with Sidebar
const DashboardLayout = ({ children }) => {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};

function App() {
  const { isAuthenticated, loading, homeSetupComplete } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Routes>
      {/* Public Route */}
      <Route 
        path="/login" 
        element={
          isAuthenticated 
            ? <Navigate to={homeSetupComplete ? "/dashboard" : "/setup"} replace /> 
            : <LoginPage />
        } 
      />

      {/* Home Setup Route */}
      <Route 
        path="/setup" 
        element={
          !isAuthenticated 
            ? <Navigate to="/login" replace />
            : homeSetupComplete 
              ? <Navigate to="/dashboard" replace />
              : <HomeSetupPage />
        } 
      />

      {/* Protected Routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <Dashboard />
            </DashboardLayout>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/sources" 
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <SourcesPage />
            </DashboardLayout>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/alerts" 
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <AlertsPage />
            </DashboardLayout>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/analytics" 
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <AnalyticsPage />
            </DashboardLayout>
          </ProtectedRoute>
        } 
      />

      <Route 
        path="/settings" 
        element={
          <ProtectedRoute>
            <DashboardLayout>
              <SettingsPage />
            </DashboardLayout>
          </ProtectedRoute>
        } 
      />

      {/* Default Redirect */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
