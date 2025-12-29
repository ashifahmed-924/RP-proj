/**
 * Main Layout Component
 * Provides consistent navigation and structure
 */

import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Layout.css';

const Layout = ({ children }) => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getRoleBadgeClass = (role) => {
    switch (role) {
      case 'admin': return 'nav-badge-admin';
      case 'teacher': return 'nav-badge-teacher';
      case 'student': return 'nav-badge-student';
      default: return '';
    }
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/dashboard" className="nav-brand">
            <span className="nav-logo">📚</span>
            <span className="nav-title">EduLearn</span>
          </Link>

          <div className="nav-links">
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/progress" className="nav-link">Progress</Link>
            {user?.role === 'student' && (
              <Link to="/dashboard" className="nav-link">My Modules</Link>
            )}
            {(user?.role === 'teacher' || isAdmin) && (
              <>
                <Link to="/ecese/upload" className="nav-link">Upload Content</Link>
                <Link to="/analytics" className="nav-link">Analytics</Link>
              </>
            )}
            {isAdmin && (
              <Link to="/admin/users" className="nav-link">Users</Link>
            )}
          </div>

          <div className="nav-user">
            <div className="nav-user-info">
              <span className="nav-user-name">{user?.full_name}</span>
              <span className={`nav-badge ${getRoleBadgeClass(user?.role)}`}>
                {user?.role}
              </span>
            </div>
            <div className="nav-dropdown">
              <button className="nav-avatar">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </button>
              <div className="nav-dropdown-content">
                <Link to="/account/edit" className="dropdown-item">
                  <span className="dropdown-icon">⚙️</span>
                  Account Settings
                </Link>
                <button onClick={handleLogout} className="dropdown-item dropdown-logout">
                  <span className="dropdown-icon">🚪</span>
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {children}
      </main>

      <footer className="footer">
        <p>© 2024 EduLearn. Built with ❤️ for learners.</p>
      </footer>
    </div>
  );
};

export default Layout;


