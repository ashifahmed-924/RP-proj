"""
Models package.
Contains data models for the e-learning application.
"""

from .user import User, UserRole
from .streak import Streak, EngagementLog
from .badge import Badge, UserBadge, BadgeCategory, BadgeRarity, DEFAULT_BADGES
from .leaderboard import LeaderboardEntry, UserPoints, LeaderboardType

__all__ = [
    'User', 'UserRole',
    'Streak', 'EngagementLog',
    'Badge', 'UserBadge', 'BadgeCategory', 'BadgeRarity', 'DEFAULT_BADGES',
    'LeaderboardEntry', 'UserPoints', 'LeaderboardType'
]


