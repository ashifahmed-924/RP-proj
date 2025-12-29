/**
 * Progress Dashboard Component
 * Main PMSAS dashboard showing streaks, badges, and leaderboards
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import pmsasService from '../../services/pmsasService';
import Layout from '../layout/Layout';
import './PMSASStyles.css';

const ProgressDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [badges, setBadges] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summaryRes, leaderboardRes, badgesRes, analyticsRes] = await Promise.all([
        pmsasService.getSummary(),
        pmsasService.getLeaderboard('streak', 10),
        pmsasService.getMyBadges(),
        pmsasService.getMyAnalytics()
      ]);
      
      setSummary(summaryRes.summary);
      setLeaderboard(leaderboardRes.leaderboard);
      setBadges(badgesRes.badges);
      setAnalytics(analyticsRes.analytics);
    } catch (err) {
      console.error('Failed to load PMSAS data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRarityClass = (rarity) => {
    return `rarity-${rarity}`;
  };

  if (loading) {
    return (
      <Layout>
        <div className="pmsas-loading">
          <div className="loading-spinner"></div>
          <p>Loading your progress...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="pmsas-dashboard">
        {/* Header with Streak Fire */}
        <div className="pmsas-header">
          <div className="streak-hero">
            <div className={`streak-fire ${summary?.current_streak > 0 ? 'active' : ''}`}>
              <span className="fire-icon">🔥</span>
              <span className="streak-count">{summary?.current_streak || 0}</span>
            </div>
            <div className="streak-info">
              <h1>Day Streak</h1>
              <p>Longest: {summary?.longest_streak || 0} days</p>
              {summary?.is_at_risk && (
                <div className="streak-warning">
                  ⚠️ Your streak is at risk! Complete an activity today.
                </div>
              )}
            </div>
          </div>
          
          <div className="quick-stats">
            <div className="stat-item">
              <span className="stat-icon">⭐</span>
              <div className="stat-details">
                <span className="stat-value">{summary?.total_points || 0}</span>
                <span className="stat-label">Points</span>
              </div>
            </div>
            <div className="stat-item">
              <span className="stat-icon">🎖️</span>
              <div className="stat-details">
                <span className="stat-value">Lvl {summary?.level || 1}</span>
                <span className="stat-label">Level</span>
              </div>
            </div>
            <div className="stat-item">
              <span className="stat-icon">🏅</span>
              <div className="stat-details">
                <span className="stat-value">{summary?.badges_earned || 0}</span>
                <span className="stat-label">Badges</span>
              </div>
            </div>
            <div className="stat-item">
              <span className="stat-icon">📅</span>
              <div className="stat-details">
                <span className="stat-value">{summary?.total_active_days || 0}</span>
                <span className="stat-label">Active Days</span>
              </div>
            </div>
          </div>
        </div>

        {/* Level Progress Bar */}
        <div className="level-progress-card">
          <div className="level-info">
            <span>Level {summary?.level || 1}</span>
            <span>{summary?.level_progress || 0}% to Level {(summary?.level || 1) + 1}</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${summary?.level_progress || 0}%` }}
            ></div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="pmsas-tabs">
          <button 
            className={`pmsas-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`pmsas-tab ${activeTab === 'badges' ? 'active' : ''}`}
            onClick={() => setActiveTab('badges')}
          >
            🏆 Badges
          </button>
          <button 
            className={`pmsas-tab ${activeTab === 'leaderboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('leaderboard')}
          >
            📈 Leaderboard
          </button>
          <button 
            className={`pmsas-tab ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            💡 Insights
          </button>
        </div>

        {/* Tab Content */}
        <div className="pmsas-content">
          {activeTab === 'overview' && (
            <div className="overview-grid">
              {/* Engagement Chart Placeholder */}
              <div className="chart-card">
                <h3>📅 Activity This Month</h3>
                <div className="activity-calendar">
                  {[...Array(30)].map((_, i) => (
                    <div 
                      key={i} 
                      className={`calendar-day ${Math.random() > 0.5 ? 'active' : ''}`}
                      title={`Day ${i + 1}`}
                    ></div>
                  ))}
                </div>
                <div className="calendar-legend">
                  <span><span className="legend-box inactive"></span> No activity</span>
                  <span><span className="legend-box active"></span> Active</span>
                </div>
              </div>

              {/* Recent Badges */}
              <div className="recent-badges-card">
                <h3>🎖️ Recent Badges</h3>
                {badges.length > 0 ? (
                  <div className="badges-mini-grid">
                    {badges.slice(0, 4).map((badge, idx) => (
                      <div key={idx} className={`badge-mini ${getRarityClass(badge.rarity)}`}>
                        <span className="badge-icon">{badge.icon}</span>
                        <span className="badge-name">{badge.name}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-badges">
                    <span>🎯</span>
                    <p>Complete activities to earn badges!</p>
                  </div>
                )}
              </div>

              {/* Top Streakers */}
              <div className="top-streakers-card">
                <h3>🔥 Top Streakers</h3>
                <div className="mini-leaderboard">
                  {leaderboard?.entries?.slice(0, 5).map((entry, idx) => (
                    <div key={idx} className="mini-leader-row">
                      <span className="rank">#{idx + 1}</span>
                      <span className="name">{entry.user_name}</span>
                      <span className="score">{entry.score} 🔥</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Predictions */}
              {analytics?.predictions && (
                <div className="predictions-card">
                  <h3>🔮 Your Learning Insights</h3>
                  <div className="prediction-stats">
                    <div className="prediction-item">
                      <span className="prediction-label">Engagement</span>
                      <span className={`prediction-value ${analytics.predictions.engagement_level}`}>
                        {analytics.predictions.engagement_level.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="prediction-item">
                      <span className="prediction-label">Consistency</span>
                      <span className="prediction-value">
                        {analytics.predictions.consistency_score}%
                      </span>
                    </div>
                    <div className="prediction-item">
                      <span className="prediction-label">Trend</span>
                      <span className={`prediction-value trend-${analytics.predictions.trend}`}>
                        {analytics.predictions.trend === 'increasing' ? '📈' : 
                         analytics.predictions.trend === 'decreasing' ? '📉' : '➡️'}
                        {analytics.predictions.trend}
                      </span>
                    </div>
                  </div>
                  <div className="recommendations">
                    <h4>💡 Recommendations</h4>
                    <ul>
                      {analytics.predictions.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'badges' && (
            <div className="badges-section">
              <h2>Your Badges</h2>
              {badges.length > 0 ? (
                <div className="badges-grid">
                  {badges.map((badge, idx) => (
                    <div 
                      key={idx} 
                      className={`badge-card ${getRarityClass(badge.rarity)} ${badge.earned_at ? 'earned' : 'locked'}`}
                    >
                      <div className="badge-icon-large">{badge.icon}</div>
                      <h4>{badge.name}</h4>
                      <p>{badge.description}</p>
                      <div className="badge-meta">
                        <span className={`rarity-tag ${badge.rarity}`}>{badge.rarity}</span>
                        <span className="points-tag">+{badge.points_value} pts</span>
                      </div>
                      {badge.earned_at && (
                        <div className="earned-date">
                          Earned {new Date(badge.earned_at).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <span className="empty-icon">🏆</span>
                  <p>No badges earned yet</p>
                  <span className="empty-hint">Complete learning activities to earn your first badge!</span>
                </div>
              )}
            </div>
          )}

          {activeTab === 'leaderboard' && (
            <div className="leaderboard-section">
              <h2>🏆 Streak Leaderboard</h2>
              <div className="leaderboard-table">
                {leaderboard?.entries?.map((entry, idx) => (
                  <div 
                    key={idx} 
                    className={`leaderboard-row ${entry.user_id === user?.id ? 'current-user' : ''}`}
                  >
                    <div className="rank-badge">
                      {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx + 1}`}
                    </div>
                    <div className="user-info">
                      <div className="user-avatar-small">
                        {entry.user_name?.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span className="user-name">{entry.user_name}</span>
                      {entry.user_id === user?.id && <span className="you-tag">You</span>}
                    </div>
                    <div className="score-info">
                      <span className="streak-score">{entry.score} 🔥</span>
                      <span className="secondary-score">Best: {entry.secondary_score}</span>
                    </div>
                  </div>
                ))}
              </div>
              
              {leaderboard?.user_rank && leaderboard.user_rank > 10 && (
                <div className="your-position">
                  <span>Your Position: #{leaderboard.user_rank} of {leaderboard.total_participants}</span>
                </div>
              )}
            </div>
          )}

          {activeTab === 'insights' && analytics && (
            <div className="insights-section">
              <h2>📊 Your Learning Analytics</h2>
              
              <div className="insights-grid">
                <div className="insight-card">
                  <h3>Engagement Summary (30 days)</h3>
                  <div className="insight-stats">
                    <div className="insight-stat">
                      <span className="value">{analytics.engagement.total_activities_30d}</span>
                      <span className="label">Total Activities</span>
                    </div>
                    <div className="insight-stat">
                      <span className="value">
                        {Math.round(analytics.engagement.total_time_seconds_30d / 60)}
                      </span>
                      <span className="label">Minutes Learned</span>
                    </div>
                    <div className="insight-stat">
                      <span className="value">
                        {analytics.engagement.avg_daily_activities.toFixed(1)}
                      </span>
                      <span className="label">Avg Daily Activities</span>
                    </div>
                  </div>
                </div>

                <div className="insight-card">
                  <h3>Activity Breakdown</h3>
                  <div className="activity-breakdown">
                    {Object.entries(analytics.engagement.activity_breakdown || {}).map(([type, count]) => (
                      <div key={type} className="breakdown-item">
                        <span className="type">{type.replace('_', ' ')}</span>
                        <div className="breakdown-bar">
                          <div 
                            className="breakdown-fill"
                            style={{ 
                              width: `${(count / analytics.engagement.total_activities_30d) * 100}%` 
                            }}
                          ></div>
                        </div>
                        <span className="count">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="insight-card risk-card">
                  <h3>Dropout Risk Assessment</h3>
                  <div className={`risk-indicator ${analytics.predictions.risk_of_dropout}`}>
                    <span className="risk-level">{analytics.predictions.risk_of_dropout}</span>
                    <span className="risk-score">Score: {analytics.predictions.risk_score}/100</span>
                  </div>
                  <p className="risk-description">
                    {analytics.predictions.risk_of_dropout === 'low' 
                      ? "Great job! You're maintaining consistent learning habits."
                      : analytics.predictions.risk_of_dropout === 'medium'
                      ? "Your engagement could use a boost. Try setting daily reminders."
                      : "We've noticed a drop in activity. Let's get back on track!"}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default ProgressDashboard;





