/**
 * Leaderboard Component
 * Displays rankings and user positions
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import pmsasService from '../../services/pmsasService';
import './PMSASStyles.css';

const Leaderboard = ({ courseId = null }) => {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [myRank, setMyRank] = useState(null);
  const [period, setPeriod] = useState('weekly');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, [period, courseId]);

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const data = await pmsasService.getLeaderboard({
        period,
        limit: 10,
        course_id: courseId
      });
      
      setLeaderboard(data.leaderboard);
      setMyRank(data.my_rank);
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return `#${rank}`;
    }
  };

  const getPeriodLabel = () => {
    switch (period) {
      case 'daily': return 'Today';
      case 'weekly': return 'This Week';
      case 'monthly': return 'This Month';
      case 'all_time': return 'All Time';
      default: return '';
    }
  };

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <h3>🏆 Leaderboard</h3>
        <select 
          value={period} 
          onChange={(e) => setPeriod(e.target.value)}
          className="period-select"
        >
          <option value="daily">Today</option>
          <option value="weekly">This Week</option>
          <option value="monthly">This Month</option>
          <option value="all_time">All Time</option>
        </select>
      </div>

      <p className="leaderboard-period">{getPeriodLabel()}</p>

      {loading ? (
        <div className="leaderboard-loading">Loading...</div>
      ) : leaderboard.length === 0 ? (
        <div className="leaderboard-empty">
          <span className="empty-icon">📊</span>
          <p>No data yet for {getPeriodLabel().toLowerCase()}</p>
        </div>
      ) : (
        <div className="leaderboard-list">
          {leaderboard.map((entry, index) => {
            const isCurrentUser = entry.user_id === user?.id;
            return (
              <div 
                key={entry.user_id}
                className={`leaderboard-entry ${isCurrentUser ? 'current-user' : ''} ${index < 3 ? 'top-three' : ''}`}
              >
                <span className="entry-rank">{getRankIcon(entry.rank)}</span>
                <div className="entry-user">
                  <span className="entry-name">
                    {entry.user_name}
                    {isCurrentUser && <span className="you-badge">You</span>}
                  </span>
                  <span className="entry-stats">
                    🔥 {entry.current_streak} day streak • {entry.activities_count} activities
                  </span>
                </div>
                <div className="entry-points">
                  <span className="points-value">{entry.total_points}</span>
                  <span className="points-label">pts</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {myRank && !leaderboard.find(e => e.user_id === user?.id) && (
        <div className="my-rank-section">
          <p className="my-rank-label">Your Position</p>
          <div className="leaderboard-entry current-user">
            <span className="entry-rank">#{myRank.rank}</span>
            <div className="entry-user">
              <span className="entry-name">{myRank.user_name}</span>
              <span className="entry-stats">
                🔥 {myRank.current_streak} day streak
              </span>
            </div>
            <div className="entry-points">
              <span className="points-value">{myRank.total_points}</span>
              <span className="points-label">pts</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Leaderboard;


