"""
Streak Model Module.
Defines models for tracking learning streaks and daily engagement.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from bson import ObjectId


class Streak:
    """
    Streak model for tracking daily learning consistency.
    
    Attributes:
        _id: MongoDB ObjectId
        user_id: Reference to user
        current_streak: Current consecutive days
        longest_streak: Best streak achieved
        last_activity_date: Date of last recorded activity
        streak_start_date: When current streak began
        total_active_days: Total days with activity
        streak_history: List of past streaks with dates
        is_at_risk: Whether streak might break soon
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    
    COLLECTION_NAME = 'streaks'
    
    def __init__(
        self,
        user_id: ObjectId,
        current_streak: int = 0,
        longest_streak: int = 0,
        last_activity_date: Optional[datetime] = None,
        streak_start_date: Optional[datetime] = None,
        total_active_days: int = 0,
        streak_history: Optional[List[Dict]] = None,
        is_at_risk: bool = False,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.last_activity_date = last_activity_date
        self.streak_start_date = streak_start_date
        self.total_active_days = total_active_days
        self.streak_history = streak_history or []
        self.is_at_risk = is_at_risk
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert streak to dictionary."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date,
            'streak_start_date': self.streak_start_date,
            'total_active_days': self.total_active_days,
            'streak_history': self.streak_history,
            'is_at_risk': self.is_at_risk,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'user_id': str(self.user_id),
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'streak_start_date': self.streak_start_date.isoformat() if self.streak_start_date else None,
            'total_active_days': self.total_active_days,
            'streak_history': self.streak_history,
            'is_at_risk': self.is_at_risk,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Streak':
        """Create a Streak instance from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            current_streak=data.get('current_streak', 0),
            longest_streak=data.get('longest_streak', 0),
            last_activity_date=data.get('last_activity_date'),
            streak_start_date=data.get('streak_start_date'),
            total_active_days=data.get('total_active_days', 0),
            streak_history=data.get('streak_history', []),
            is_at_risk=data.get('is_at_risk', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class EngagementLog:
    """
    Engagement log for tracking individual learning activities.
    
    Attributes:
        _id: MongoDB ObjectId
        user_id: Reference to user
        activity_type: Type of activity (quiz, lesson, login, etc.)
        activity_id: Reference to the activity
        duration_seconds: Time spent on activity
        points_earned: Points from this activity
        metadata: Additional activity-specific data
        created_at: When activity occurred
    """
    
    COLLECTION_NAME = 'engagement_logs'
    
    ACTIVITY_TYPES = [
        'login',
        'quiz_complete',
        'lesson_complete',
        'video_watched',
        'assignment_submit',
        'discussion_post',
        'resource_access'
    ]
    
    def __init__(
        self,
        user_id: ObjectId,
        activity_type: str,
        activity_id: Optional[ObjectId] = None,
        duration_seconds: int = 0,
        points_earned: int = 0,
        metadata: Optional[Dict] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.activity_type = activity_type
        self.activity_id = activity_id
        self.duration_seconds = duration_seconds
        self.points_earned = points_earned
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'activity_id': self.activity_id,
            'duration_seconds': self.duration_seconds,
            'points_earned': self.points_earned,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'user_id': str(self.user_id),
            'activity_type': self.activity_type,
            'activity_id': str(self.activity_id) if self.activity_id else None,
            'duration_seconds': self.duration_seconds,
            'points_earned': self.points_earned,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EngagementLog':
        """Create from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            activity_type=data['activity_type'],
            activity_id=data.get('activity_id'),
            duration_seconds=data.get('duration_seconds', 0),
            points_earned=data.get('points_earned', 0),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at')
        )





