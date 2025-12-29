"""
PMSAS Models Module.

Progress Monitoring and Streak Analytics System data models.
Includes: Streaks, Badges, Activities, Leaderboard entries.

Based on research by W.M.P.S. Weerasekara (IT22215406)
Project ID: 25-26j-233
"""

from enum import Enum
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from bson import ObjectId


class ActivityType(str, Enum):
    """Types of learning activities that count towards streaks."""
    
    LOGIN = 'login'
    QUIZ_COMPLETED = 'quiz_completed'
    LESSON_COMPLETED = 'lesson_completed'
    ASSIGNMENT_SUBMITTED = 'assignment_submitted'
    VIDEO_WATCHED = 'video_watched'
    DISCUSSION_POST = 'discussion_post'
    STUDY_SESSION = 'study_session'


class BadgeType(str, Enum):
    """Types of badges/awards for gamification."""
    
    # Streak badges
    STREAK_3_DAYS = 'streak_3_days'
    STREAK_7_DAYS = 'streak_7_days'
    STREAK_14_DAYS = 'streak_14_days'
    STREAK_30_DAYS = 'streak_30_days'
    STREAK_60_DAYS = 'streak_60_days'
    STREAK_100_DAYS = 'streak_100_days'
    
    # Achievement badges
    FIRST_QUIZ = 'first_quiz'
    QUIZ_MASTER = 'quiz_master'
    PERFECT_SCORE = 'perfect_score'
    FAST_LEARNER = 'fast_learner'
    CONSISTENT_LEARNER = 'consistent_learner'
    TOP_PERFORMER = 'top_performer'
    EARLY_BIRD = 'early_bird'
    NIGHT_OWL = 'night_owl'
    
    # Social badges
    HELPFUL_PEER = 'helpful_peer'
    DISCUSSION_STARTER = 'discussion_starter'


BADGE_DEFINITIONS = {
    BadgeType.STREAK_3_DAYS: {
        'name': '3-Day Streak',
        'description': 'Maintained a learning streak for 3 consecutive days',
        'icon': '🔥',
        'points': 50
    },
    BadgeType.STREAK_7_DAYS: {
        'name': 'Week Warrior',
        'description': 'Maintained a learning streak for 7 consecutive days',
        'icon': '⭐',
        'points': 100
    },
    BadgeType.STREAK_14_DAYS: {
        'name': 'Fortnight Fighter',
        'description': 'Maintained a learning streak for 14 consecutive days',
        'icon': '🏆',
        'points': 200
    },
    BadgeType.STREAK_30_DAYS: {
        'name': 'Monthly Master',
        'description': 'Maintained a learning streak for 30 consecutive days',
        'icon': '👑',
        'points': 500
    },
    BadgeType.STREAK_60_DAYS: {
        'name': 'Dedication Champion',
        'description': 'Maintained a learning streak for 60 consecutive days',
        'icon': '💎',
        'points': 1000
    },
    BadgeType.STREAK_100_DAYS: {
        'name': 'Century Legend',
        'description': 'Maintained a learning streak for 100 consecutive days',
        'icon': '🌟',
        'points': 2000
    },
    BadgeType.FIRST_QUIZ: {
        'name': 'Quiz Beginner',
        'description': 'Completed your first quiz',
        'icon': '📝',
        'points': 25
    },
    BadgeType.QUIZ_MASTER: {
        'name': 'Quiz Master',
        'description': 'Completed 50 quizzes',
        'icon': '🎯',
        'points': 300
    },
    BadgeType.PERFECT_SCORE: {
        'name': 'Perfectionist',
        'description': 'Achieved a perfect score on a quiz',
        'icon': '💯',
        'points': 150
    },
    BadgeType.FAST_LEARNER: {
        'name': 'Fast Learner',
        'description': 'Completed 5 lessons in a single day',
        'icon': '⚡',
        'points': 100
    },
    BadgeType.CONSISTENT_LEARNER: {
        'name': 'Consistent Learner',
        'description': 'Studied at the same time for 7 days',
        'icon': '🎖️',
        'points': 150
    },
    BadgeType.TOP_PERFORMER: {
        'name': 'Top Performer',
        'description': 'Ranked #1 on the weekly leaderboard',
        'icon': '🥇',
        'points': 500
    },
    BadgeType.EARLY_BIRD: {
        'name': 'Early Bird',
        'description': 'Started learning before 7 AM for 5 days',
        'icon': '🌅',
        'points': 75
    },
    BadgeType.NIGHT_OWL: {
        'name': 'Night Owl',
        'description': 'Studied after 10 PM for 5 days',
        'icon': '🦉',
        'points': 75
    },
    BadgeType.HELPFUL_PEER: {
        'name': 'Helpful Peer',
        'description': 'Helped 10 classmates in discussions',
        'icon': '🤝',
        'points': 200
    },
    BadgeType.DISCUSSION_STARTER: {
        'name': 'Discussion Starter',
        'description': 'Started 5 meaningful discussions',
        'icon': '💬',
        'points': 100
    }
}


class LearningActivity:
    """
    Model for tracking individual learning activities.
    
    Each activity contributes to streak calculation and analytics.
    """
    
    COLLECTION_NAME = 'learning_activities'
    
    def __init__(
        self,
        user_id: ObjectId,
        activity_type: ActivityType,
        course_id: Optional[ObjectId] = None,
        lesson_id: Optional[ObjectId] = None,
        quiz_id: Optional[ObjectId] = None,
        score: Optional[float] = None,
        duration_minutes: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.activity_type = activity_type if isinstance(activity_type, ActivityType) else ActivityType(activity_type)
        self.course_id = course_id
        self.lesson_id = lesson_id
        self.quiz_id = quiz_id
        self.score = score
        self.duration_minutes = duration_minutes
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.activity_date = self.created_at.date()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'activity_type': self.activity_type.value,
            'course_id': self.course_id,
            'lesson_id': self.lesson_id,
            'quiz_id': self.quiz_id,
            'score': self.score,
            'duration_minutes': self.duration_minutes,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'activity_date': self.created_at.strftime('%Y-%m-%d')
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'user_id': str(self.user_id),
            'activity_type': self.activity_type.value,
            'course_id': str(self.course_id) if self.course_id else None,
            'lesson_id': str(self.lesson_id) if self.lesson_id else None,
            'quiz_id': str(self.quiz_id) if self.quiz_id else None,
            'score': self.score,
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningActivity':
        """Create instance from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            activity_type=data['activity_type'],
            course_id=data.get('course_id'),
            lesson_id=data.get('lesson_id'),
            quiz_id=data.get('quiz_id'),
            score=data.get('score'),
            duration_minutes=data.get('duration_minutes', 0),
            metadata=data.get('metadata'),
            created_at=data.get('created_at')
        )


class UserStreak:
    """
    Model for tracking user learning streaks.
    
    Implements streak mechanics based on daily activity tracking.
    """
    
    COLLECTION_NAME = 'user_streaks'
    
    def __init__(
        self,
        user_id: ObjectId,
        current_streak: int = 0,
        longest_streak: int = 0,
        total_active_days: int = 0,
        last_activity_date: Optional[date] = None,
        streak_start_date: Optional[date] = None,
        freeze_available: int = 2,
        freeze_used_this_month: int = 0,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.current_streak = current_streak
        self.longest_streak = longest_streak
        self.total_active_days = total_active_days
        self.last_activity_date = last_activity_date
        self.streak_start_date = streak_start_date
        self.freeze_available = freeze_available
        self.freeze_used_this_month = freeze_used_this_month
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_active_days': self.total_active_days,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'streak_start_date': self.streak_start_date.isoformat() if self.streak_start_date else None,
            'freeze_available': self.freeze_available,
            'freeze_used_this_month': self.freeze_used_this_month,
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
            'total_active_days': self.total_active_days,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'streak_start_date': self.streak_start_date.isoformat() if self.streak_start_date else None,
            'freeze_available': self.freeze_available,
            'streak_at_risk': self._is_streak_at_risk(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def _is_streak_at_risk(self) -> bool:
        """Check if streak is at risk of breaking."""
        if not self.last_activity_date:
            return False
        today = date.today()
        days_since_activity = (today - self.last_activity_date).days
        return days_since_activity >= 1 and self.current_streak > 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStreak':
        """Create instance from dictionary."""
        last_activity = data.get('last_activity_date')
        streak_start = data.get('streak_start_date')
        
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            current_streak=data.get('current_streak', 0),
            longest_streak=data.get('longest_streak', 0),
            total_active_days=data.get('total_active_days', 0),
            last_activity_date=date.fromisoformat(last_activity) if last_activity else None,
            streak_start_date=date.fromisoformat(streak_start) if streak_start else None,
            freeze_available=data.get('freeze_available', 2),
            freeze_used_this_month=data.get('freeze_used_this_month', 0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class UserBadge:
    """
    Model for tracking user earned badges.
    """
    
    COLLECTION_NAME = 'user_badges'
    
    def __init__(
        self,
        user_id: ObjectId,
        badge_type: BadgeType,
        _id: Optional[ObjectId] = None,
        earned_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.badge_type = badge_type if isinstance(badge_type, BadgeType) else BadgeType(badge_type)
        self.earned_at = earned_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'badge_type': self.badge_type.value,
            'earned_at': self.earned_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        badge_info = BADGE_DEFINITIONS.get(self.badge_type, {})
        return {
            'id': str(self._id),
            'badge_type': self.badge_type.value,
            'name': badge_info.get('name', self.badge_type.value),
            'description': badge_info.get('description', ''),
            'icon': badge_info.get('icon', '🏅'),
            'points': badge_info.get('points', 0),
            'earned_at': self.earned_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserBadge':
        """Create instance from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            badge_type=data['badge_type'],
            earned_at=data.get('earned_at')
        )


class LeaderboardEntry:
    """
    Model for leaderboard entries.
    Calculated periodically (daily/weekly/monthly).
    """
    
    COLLECTION_NAME = 'leaderboard'
    
    def __init__(
        self,
        user_id: ObjectId,
        period_type: str,  # 'daily', 'weekly', 'monthly', 'all_time'
        period_start: date,
        period_end: date,
        total_points: int = 0,
        streak_days: int = 0,
        activities_count: int = 0,
        quizzes_completed: int = 0,
        average_score: float = 0.0,
        rank: int = 0,
        _id: Optional[ObjectId] = None,
        calculated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.period_type = period_type
        self.period_start = period_start
        self.period_end = period_end
        self.total_points = total_points
        self.streak_days = streak_days
        self.activities_count = activities_count
        self.quizzes_completed = quizzes_completed
        self.average_score = average_score
        self.rank = rank
        self.calculated_at = calculated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'period_type': self.period_type,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'total_points': self.total_points,
            'streak_days': self.streak_days,
            'activities_count': self.activities_count,
            'quizzes_completed': self.quizzes_completed,
            'average_score': self.average_score,
            'rank': self.rank,
            'calculated_at': self.calculated_at
        }
    
    def to_response_dict(self, user_name: str = None) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'user_id': str(self.user_id),
            'user_name': user_name,
            'period_type': self.period_type,
            'total_points': self.total_points,
            'streak_days': self.streak_days,
            'activities_count': self.activities_count,
            'average_score': round(self.average_score, 1),
            'rank': self.rank
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LeaderboardEntry':
        """Create instance from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            period_type=data['period_type'],
            period_start=date.fromisoformat(data['period_start']),
            period_end=date.fromisoformat(data['period_end']),
            total_points=data.get('total_points', 0),
            streak_days=data.get('streak_days', 0),
            activities_count=data.get('activities_count', 0),
            quizzes_completed=data.get('quizzes_completed', 0),
            average_score=data.get('average_score', 0.0),
            rank=data.get('rank', 0),
            calculated_at=data.get('calculated_at')
        )






