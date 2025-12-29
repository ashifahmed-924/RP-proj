/**
 * Streak Card Component
 * Displays user's current streak with visual indicators
 */

import { useState, useEffect } from 'react';
import pmsasService from '../../services/pmsasService';
import './PMSASStyles.css';

const StreakCard = ({ compact = false }) => {
  const [streak, setStreak] = useState(null);
  const [loading, setLoading] = useState(true);
  const [freezing, setFreezing] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchStreak();
  }, []);

  const fetchStreak = async () => {
    try {
      const data = await pmsasService.getStreak();
      setStreak(data.streak);
    } catch (err) {
      console.error('Failed to fetch streak:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUseFreeze = async () => {
    if (!window.confirm('Use a streak freeze to protect your streak for today?')) {
      return;
    }

    setFreezing(true);
    try {
      const data = await pmsasService.useStreakFreeze();
      setStreak(data.streak);
      setMessage('Streak freeze applied! ❄️');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to apply freeze');
    } finally {
      setFreezing(false);
    }
  };

  const getStreakEmoji = (days) => {
    if (days >= 100) return '🌟';
    if (days >= 60) return '💎';
    if (days >= 30) return '👑';
    if (days >= 14) return '🏆';
    if (days >= 7) return '⭐';
    if (days >= 3) return '🔥';
    return '✨';
  };

  const getStreakMessage = (days) => {
    if (days >= 100) return 'Legendary!';
    if (days >= 60) return 'Incredible!';
    if (days >= 30) return 'Amazing!';
    if (days >= 14) return 'Great job!';
    if (days >= 7) return 'On fire!';
    if (days >= 3) return 'Keep going!';
    if (days > 0) return 'Good start!';
    return 'Start your streak!';
  };

  if (loading) {
    return (
      <div className={`streak-card ${compact ? 'streak-card-compact' : ''}`}>
        <div className="streak-loading">Loading...</div>
      </div>
    );
  }

  if (compact) {
    return (
      <div className="streak-card streak-card-compact">
        <div className="streak-compact-content">
          <span className="streak-emoji">{getStreakEmoji(streak?.current_streak || 0)}</span>
          <span className="streak-days">{streak?.current_streak || 0}</span>
          <span className="streak-label">day streak</span>
        </div>
      </div>
    );
  }

  return (
    <div className="streak-card">
      <div className="streak-header">
        <h3>Your Learning Streak</h3>
        {streak?.streak_at_risk && (
          <span className="streak-warning">⚠️ At Risk!</span>
        )}
      </div>

      <div className="streak-main">
        <div className="streak-circle">
          <span className="streak-emoji-large">{getStreakEmoji(streak?.current_streak || 0)}</span>
          <span className="streak-count">{streak?.current_streak || 0}</span>
          <span className="streak-unit">days</span>
        </div>
        <p className="streak-message">{getStreakMessage(streak?.current_streak || 0)}</p>
      </div>

      <div className="streak-stats">
        <div className="streak-stat">
          <span className="stat-value">{streak?.longest_streak || 0}</span>
          <span className="stat-label">Longest</span>
        </div>
        <div className="streak-stat">
          <span className="stat-value">{streak?.total_active_days || 0}</span>
          <span className="stat-label">Total Days</span>
        </div>
        <div className="streak-stat">
          <span className="stat-value">{streak?.freeze_available || 0}</span>
          <span className="stat-label">Freezes</span>
        </div>
      </div>

      {streak?.streak_at_risk && streak?.freeze_available > 0 && (
        <div className="streak-freeze">
          <button 
            className="btn btn-freeze" 
            onClick={handleUseFreeze}
            disabled={freezing}
          >
            ❄️ {freezing ? 'Applying...' : 'Use Streak Freeze'}
          </button>
        </div>
      )}

      {message && (
        <div className="streak-message-alert">{message}</div>
      )}
    </div>
  );
};

export default StreakCard;


