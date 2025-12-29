/**
 * Main App Component
 * Configures routing and authentication context
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';

// Account Components
import { LoginPage, RegisterPage, AccountEditPage } from './components/accounts';

// Dashboard
import Dashboard from './components/dashboard/Dashboard';

// Admin Components
import AdminUsersPage from './components/admin/AdminUsersPage';

// PMSAS Components
import { ProgressDashboard, TeacherAnalytics } from './components/pmsas';

// ECESE Components
import { TeacherUploadPage, StudentContentViewer } from './components/ecese';

// Global Styles
import './App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/account/edit" 
            element={
              <ProtectedRoute>
                <AccountEditPage />
              </ProtectedRoute>
            } 
          />
          
          {/* PMSAS Routes */}
          <Route 
            path="/progress" 
            element={
              <ProtectedRoute>
                <ProgressDashboard />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute>
                <TeacherAnalytics />
              </ProtectedRoute>
            } 
          />
          
          {/* Admin Routes */}
          <Route 
            path="/admin/users" 
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminUsersPage />
              </ProtectedRoute>
            } 
          />
          
          {/* ECESE Routes */}
          <Route 
            path="/ecese/upload" 
            element={
              <ProtectedRoute>
                <TeacherUploadPage />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/modules/:moduleName/content" 
            element={
              <ProtectedRoute>
                <StudentContentViewer />
              </ProtectedRoute>
            } 
          />
          
          {/* Default Redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
