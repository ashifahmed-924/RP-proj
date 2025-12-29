/**
 * Dashboard Component
 * Main landing page after login
 */

import { useAuth } from '../../context/AuthContext';
import Layout from '../layout/Layout';
import './Dashboard.css';

const Dashboard = () => {
  const { user, isAdmin, isTeacher, isStudent } = useAuth();

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <Layout>
      <div className="dashboard">
        {/* Welcome Section */}
        <div className="dashboard-header">
          <div className="welcome-text">
            <h1>{getWelcomeMessage()}, {user?.first_name}!</h1>
            <p>Welcome to your learning dashboard</p>
          </div>
          <div className="header-decoration">
            <div className="decoration-circle circle-1"></div>
            <div className="decoration-circle circle-2"></div>
            <div className="decoration-circle circle-3"></div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          {isStudent && (
            <>
              <div className="stat-card stat-courses">
                <div className="stat-icon">📖</div>
                <div className="stat-content">
                  <span className="stat-value">0</span>
                  <span className="stat-label">Enrolled Courses</span>
                </div>
              </div>
              <div className="stat-card stat-progress">
                <div className="stat-icon">📊</div>
                <div className="stat-content">
                  <span className="stat-value">0%</span>
                  <span className="stat-label">Overall Progress</span>
                </div>
              </div>
              <div className="stat-card stat-certificates">
                <div className="stat-icon">🏆</div>
                <div className="stat-content">
                  <span className="stat-value">0</span>
                  <span className="stat-label">Certificates</span>
                </div>
              </div>
            </>
          )}

          {isTeacher && (
            <>
              <div className="stat-card stat-courses">
                <div className="stat-icon">📚</div>
                <div className="stat-content">
                  <span className="stat-value">0</span>
                  <span className="stat-label">My Courses</span>
                </div>
              </div>
              <div className="stat-card stat-students">
                <div className="stat-icon">👥</div>
                <div className="stat-content">
                  <span className="stat-value">0</span>
                  <span className="stat-label">Total Students</span>
                </div>
              </div>
              <div className="stat-card stat-reviews">
                <div className="stat-icon">⭐</div>
                <div className="stat-content">
                  <span className="stat-value">0.0</span>
                  <span className="stat-label">Avg. Rating</span>
                </div>
              </div>
            </>
          )}

          {isAdmin && (
            <>
              <div className="stat-card stat-users">
                <div className="stat-icon">👤</div>
                <div className="stat-content">
                  <span className="stat-value">0</span>
                  <span className="stat-label">Total Users</span>
                </div>
              </div>
              <div className="stat-card stat-courses">
                <div className="stat-icon">📚</div>
                <div className="stat-content">
                  <span className="stat-value">0</span>
                  <span className="stat-label">Total Courses</span>
                </div>
              </div>
              <div className="stat-card stat-revenue">
                <div className="stat-icon">💰</div>
                <div className="stat-content">
                  <span className="stat-value">$0</span>
                  <span className="stat-label">Total Revenue</span>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Quick Actions */}
        <div className="section">
          <h2 className="section-title">Quick Actions</h2>
          <div className="actions-grid">
            {isStudent && (
              <>
                <button className="action-card">
                  <span className="action-icon">🔍</span>
                  <span className="action-label">Browse Courses</span>
                </button>
                <button className="action-card">
                  <span className="action-icon">📝</span>
                  <span className="action-label">Continue Learning</span>
                </button>
                <button className="action-card">
                  <span className="action-icon">📋</span>
                  <span className="action-label">My Assignments</span>
                </button>
              </>
            )}

            {isTeacher && (
              <>
                <button className="action-card">
                  <span className="action-icon">➕</span>
                  <span className="action-label">Create Course</span>
                </button>
                <button className="action-card">
                  <span className="action-icon">📊</span>
                  <span className="action-label">View Analytics</span>
                </button>
                <button className="action-card">
                  <span className="action-icon">💬</span>
                  <span className="action-label">Messages</span>
                </button>
              </>
            )}

            {isAdmin && (
              <>
                <button className="action-card">
                  <span className="action-icon">👥</span>
                  <span className="action-label">Manage Users</span>
                </button>
                <button className="action-card">
                  <span className="action-icon">📚</span>
                  <span className="action-label">Manage Courses</span>
                </button>
                <button className="action-card">
                  <span className="action-icon">📈</span>
                  <span className="action-label">View Reports</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Activity Section */}
        <div className="section">
          <h2 className="section-title">Recent Activity</h2>
          <div className="activity-card">
            <div className="empty-state">
              <span className="empty-icon">📭</span>
              <p>No recent activity yet</p>
              <span className="empty-hint">Start exploring courses to see your activity here</span>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;






