/**
 * Teacher Analytics Dashboard Component
 * PMSAS dashboard for teachers to monitor student engagement
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import pmsasService from '../../services/pmsasService';
import Layout from '../layout/Layout';
import './PMSASStyles.css';

const TeacherAnalytics = () => {
  const { isTeacher, isAdmin } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [atRiskStudents, setAtRiskStudents] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dashboardRes, atRiskRes] = await Promise.all([
        pmsasService.getTeacherDashboard(),
        pmsasService.getAtRiskStudents()
      ]);
      
      setDashboard(dashboardRes.dashboard);
      setAtRiskStudents(atRiskRes.at_risk_students);
    } catch (err) {
      console.error('Failed to load teacher dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isTeacher && !isAdmin) {
    return (
      <Layout>
        <div className="access-denied">
          <h2>Access Denied</h2>
          <p>This page is only available for teachers and administrators.</p>
        </div>
      </Layout>
    );
  }

  if (loading) {
    return (
      <Layout>
        <div className="pmsas-loading">
          <div className="loading-spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="teacher-dashboard">
        <div className="dashboard-header-simple">
          <h1>📊 Student Analytics Dashboard</h1>
          <p>Monitor student engagement and identify at-risk learners</p>
        </div>

        {/* Summary Stats */}
        <div className="teacher-stats-grid">
          <div className="teacher-stat-card">
            <div className="stat-icon-large">👥</div>
            <div className="stat-content">
              <span className="stat-number">{dashboard?.total_students || 0}</span>
              <span className="stat-title">Total Students</span>
            </div>
          </div>
          
          <div className="teacher-stat-card active">
            <div className="stat-icon-large">✅</div>
            <div className="stat-content">
              <span className="stat-number">{dashboard?.active_today || 0}</span>
              <span className="stat-title">Active Today</span>
              <span className="stat-percent">{dashboard?.active_today_percent || 0}%</span>
            </div>
          </div>
          
          <div className="teacher-stat-card warning">
            <div className="stat-icon-large">⚠️</div>
            <div className="stat-content">
              <span className="stat-number">{dashboard?.at_risk_count || 0}</span>
              <span className="stat-title">At Risk</span>
            </div>
          </div>
          
          <div className="teacher-stat-card">
            <div className="stat-icon-large">🔥</div>
            <div className="stat-content">
              <span className="stat-number">{dashboard?.avg_streak || 0}</span>
              <span className="stat-title">Avg Streak</span>
            </div>
          </div>
        </div>

        {/* Content Grid */}
        <div className="teacher-content-grid">
          {/* Streak Distribution */}
          <div className="teacher-card">
            <h3>📈 Streak Distribution</h3>
            <div className="distribution-chart">
              {Object.entries(dashboard?.streak_distribution || {}).map(([range, count]) => (
                <div key={range} className="distribution-bar-container">
                  <span className="range-label">{range} days</span>
                  <div className="distribution-bar">
                    <div 
                      className="distribution-fill"
                      style={{ 
                        width: `${(count / (dashboard?.total_students || 1)) * 100}%` 
                      }}
                    ></div>
                  </div>
                  <span className="count-label">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Performers */}
          <div className="teacher-card">
            <h3>🏆 Top Performers</h3>
            <div className="performers-list">
              {dashboard?.top_performers?.map((student, idx) => (
                <div key={idx} className="performer-row">
                  <span className="performer-rank">
                    {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`}
                  </span>
                  <span className="performer-id">{student.user_id.slice(-6)}</span>
                  <span className="performer-streak">{student.current_streak} 🔥</span>
                  <span className="performer-best">Best: {student.longest_streak}</span>
                </div>
              ))}
              {(!dashboard?.top_performers || dashboard.top_performers.length === 0) && (
                <div className="empty-list">No data available</div>
              )}
            </div>
          </div>

          {/* At-Risk Students */}
          <div className="teacher-card at-risk-card">
            <h3>🚨 Students At Risk</h3>
            <p className="card-description">
              These students haven't completed any activity today and may lose their streak.
            </p>
            <div className="at-risk-list">
              {atRiskStudents?.map((student, idx) => (
                <div key={idx} className="at-risk-row">
                  <div className="student-info">
                    <span className="student-id">Student {student.user_id.slice(-6)}</span>
                    <span className="current-streak">Current: {student.current_streak} days</span>
                  </div>
                  <div className="last-activity">
                    Last active: {student.last_activity 
                      ? new Date(student.last_activity).toLocaleDateString() 
                      : 'Never'}
                  </div>
                  <button className="btn-nudge">Send Reminder</button>
                </div>
              ))}
              {(!atRiskStudents || atRiskStudents.length === 0) && (
                <div className="empty-list success">
                  ✅ No students at risk! Everyone is on track.
                </div>
              )}
            </div>
          </div>

          {/* Engagement Insights */}
          <div className="teacher-card">
            <h3>💡 Engagement Insights</h3>
            <div className="insights-list">
              <div className="insight-item">
                <span className="insight-icon">📊</span>
                <div className="insight-content">
                  <strong>{dashboard?.active_today_percent || 0}%</strong> of students 
                  are active today
                </div>
              </div>
              <div className="insight-item">
                <span className="insight-icon">🔥</span>
                <div className="insight-content">
                  Average streak length is <strong>{dashboard?.avg_streak || 0}</strong> days
                </div>
              </div>
              <div className="insight-item">
                <span className="insight-icon">⚠️</span>
                <div className="insight-content">
                  <strong>{dashboard?.at_risk_count || 0}</strong> students need attention
                </div>
              </div>
              {dashboard?.streak_distribution?.['0'] > 0 && (
                <div className="insight-item warning">
                  <span className="insight-icon">📉</span>
                  <div className="insight-content">
                    <strong>{dashboard.streak_distribution['0']}</strong> students have 
                    no active streak
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default TeacherAnalytics;
