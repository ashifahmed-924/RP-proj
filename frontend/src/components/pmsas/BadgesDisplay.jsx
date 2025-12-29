/**
 * Badges Display Component
 * Shows earned badges and available badges
 */

import { useState, useEffect } from 'react';
import pmsasService from '../../services/pmsasService';
import './PMSASStyles.css';

const BadgesDisplay = ({ showAll = false }) => {
  const [earnedBadges, setEarnedBadges] = useState([]);
  const [availableBadges, setAvailableBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('earned');

  useEffect(() => {
    fetchBadges();
  }, []);

  const fetchBadges = async () => {
    try {
      const [earned, available] = await Promise.all([
        pmsasService.getBadges(),
        showAll ? pmsasService.getAvailableBadges() : { badges: [] }
      ]);
      
      setEarnedBadges(earned.badges);
      setAvailableBadges(available.badges);
    } catch (err) {
      console.error('Failed to fetch badges:', err);
    } finally {
      setLoading(false);
    }
  };

  const earnedBadgeTypes = new Set(earnedBadges.map(b => b.badge_type));

  if (loading) {
    return <div className="badges-loading">Loading badges...</div>;
  }

  return (
    <div className="badges-container">
      <div className="badges-header">
        <h3>🏅 Badges & Achievements</h3>
        <span className="badges-count">{earnedBadges.length} earned</span>
      </div>

      {showAll && (
        <div className="badges-tabs">
          <button 
            className={`badge-tab ${activeTab === 'earned' ? 'active' : ''}`}
            onClick={() => setActiveTab('earned')}
          >
            Earned ({earnedBadges.length})
          </button>
          <button 
            className={`badge-tab ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            All Badges ({availableBadges.length})
          </button>
        </div>
      )}

      <div className="badges-grid">
        {activeTab === 'earned' ? (
          earnedBadges.length > 0 ? (
            earnedBadges.map((badge) => (
              <div key={badge.id} className="badge-card badge-earned">
                <span className="badge-icon">{badge.icon}</span>
                <span className="badge-name">{badge.name}</span>
                <span className="badge-points">+{badge.points} pts</span>
                <span className="badge-date">
                  {new Date(badge.earned_at).toLocaleDateString()}
                </span>
              </div>
            ))
          ) : (
            <div className="badges-empty">
              <span className="empty-icon">🎯</span>
              <p>No badges earned yet</p>
              <span>Keep learning to earn your first badge!</span>
            </div>
          )
        ) : (
          availableBadges.map((badge) => {
            const isEarned = earnedBadgeTypes.has(badge.badge_type);
            return (
              <div 
                key={badge.badge_type} 
                className={`badge-card ${isEarned ? 'badge-earned' : 'badge-locked'}`}
              >
                <span className="badge-icon">{badge.icon}</span>
                <span className="badge-name">{badge.name}</span>
                <span className="badge-description">{badge.description}</span>
                <span className="badge-points">+{badge.points} pts</span>
                {isEarned && <span className="badge-check">✓</span>}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default BadgesDisplay;


