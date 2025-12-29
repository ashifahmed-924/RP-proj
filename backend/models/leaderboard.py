"""
Leaderboard Model Module.
Defines models for leaderboards and rankings.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from enum import Enum


class LeaderboardType(str, Enum):
    """Types of leaderboards."""
    STREAK = 'streak'
    POINTS = 'points'
    QUIZ_SCORE = 'quiz_score'
    COMPLETION = 'completion'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    ALL_TIME = 'all_time'


class LeaderboardEntry:
    """
    Leaderboard entry for a user's ranking.
    
    Attributes:
        _id: MongoDB ObjectId
        user_id: Reference to user
        leaderboard_type: Type of leaderboard
        scope: Scope (global, class, course)
        scope_id: ID of class/course if scoped
        score: Current score/value
        rank: Current ranking position
        previous_rank: Previous ranking for comparison
        period_start: Start of ranking period
        period_end: End of ranking period
        updated_at: Last update timestamp
    """
    
    COLLECTION_NAME = 'leaderboard_entries'
    
    def __init__(
        self,
        user_id: ObjectId,
        leaderboard_type: LeaderboardType,
        scope: str = 'global',
        scope_id: Optional[ObjectId] = None,
        score: float = 0,
        rank: int = 0,
        previous_rank: Optional[int] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        _id: Optional[ObjectId] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.leaderboard_type = leaderboard_type if isinstance(leaderboard_type, LeaderboardType) else LeaderboardType(leaderboard_type)
        self.scope = scope
        self.scope_id = scope_id
        self.score = score
        self.rank = rank
        self.previous_rank = previous_rank
        self.period_start = period_start
        self.period_end = period_end
        self.updated_at = updated_at or datetime.utcnow()
    
    @property
    def rank_change(self) -> Optional[int]:
        """Calculate rank change from previous position."""
        if self.previous_rank is None:
            return None
        return self.previous_rank - self.rank  # Positive = moved up
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'leaderboard_type': self.leaderboard_type.value,
            'scope': self.scope,
            'scope_id': self.scope_id,
            'score': self.score,
            'rank': self.rank,
            'previous_rank': self.previous_rank,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'updated_at': self.updated_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'user_id': str(self.user_id),
            'leaderboard_type': self.leaderboard_type.value,
            'scope': self.scope,
            'scope_id': str(self.scope_id) if self.scope_id else None,
            'score': self.score,
            'rank': self.rank,
            'previous_rank': self.previous_rank,
            'rank_change': self.rank_change,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeaderboardEntry':
        """Create from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            leaderboard_type=data['leaderboard_type'],
            scope=data.get('scope', 'global'),
            scope_id=data.get('scope_id'),
            score=data.get('score', 0),
            rank=data.get('rank', 0),
            previous_rank=data.get('previous_rank'),
            period_start=data.get('period_start'),
            period_end=data.get('period_end'),
            updated_at=data.get('updated_at')
        )


class UserPoints:
    """
    Model for tracking user total points.
    
    Attributes:
        _id: MongoDB ObjectId
        user_id: Reference to user
        total_points: Lifetime total points
        weekly_points: Points this week
        monthly_points: Points this month
        level: Current level based on points
        points_to_next_level: Points needed for next level
        updated_at: Last update timestamp
    """
    
    COLLECTION_NAME = 'user_points'
    
    # Level thresholds
    LEVEL_THRESHOLDS = [
        0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 11000,
        15000, 20000, 27000, 35000, 45000, 60000, 80000, 100000
    ]
    
    def __init__(
        self,
        user_id: ObjectId,
        total_points: int = 0,
        weekly_points: int = 0,
        monthly_points: int = 0,
        _id: Optional[ObjectId] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.total_points = total_points
        self.weekly_points = weekly_points
        self.monthly_points = monthly_points
        self.updated_at = updated_at or datetime.utcnow()
    
    @property
    def level(self) -> int:
        """Calculate current level based on total points."""
        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if self.total_points < threshold:
                return max(1, i)
        return len(self.LEVEL_THRESHOLDS)
    
    @property
    def points_to_next_level(self) -> int:
        """Calculate points needed for next level."""
        current_level = self.level
        if current_level >= len(self.LEVEL_THRESHOLDS):
            return 0
        return self.LEVEL_THRESHOLDS[current_level] - self.total_points
    
    @property
    def level_progress(self) -> float:
        """Calculate progress percentage to next level."""
        current_level = self.level
        if current_level >= len(self.LEVEL_THRESHOLDS):
            return 100.0
        
        prev_threshold = self.LEVEL_THRESHOLDS[current_level - 1] if current_level > 0 else 0
        next_threshold = self.LEVEL_THRESHOLDS[current_level]
        
        progress = (self.total_points - prev_threshold) / (next_threshold - prev_threshold) * 100
        return round(progress, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'total_points': self.total_points,
            'weekly_points': self.weekly_points,
            'monthly_points': self.monthly_points,
            'updated_at': self.updated_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'user_id': str(self.user_id),
            'total_points': self.total_points,
            'weekly_points': self.weekly_points,
            'monthly_points': self.monthly_points,
            'level': self.level,
            'points_to_next_level': self.points_to_next_level,
            'level_progress': self.level_progress,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPoints':
        """Create from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            total_points=data.get('total_points', 0),
            weekly_points=data.get('weekly_points', 0),
            monthly_points=data.get('monthly_points', 0),
            updated_at=data.get('updated_at')
        )





