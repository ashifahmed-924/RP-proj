"""
Badge Model Module.
Defines models for achievements, badges, and awards.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from enum import Enum


class BadgeCategory(str, Enum):
    """Categories of badges."""
    STREAK = 'streak'
    COMPLETION = 'completion'
    PERFORMANCE = 'performance'
    ENGAGEMENT = 'engagement'
    SPECIAL = 'special'


class BadgeRarity(str, Enum):
    """Rarity levels for badges."""
    COMMON = 'common'
    UNCOMMON = 'uncommon'
    RARE = 'rare'
    EPIC = 'epic'
    LEGENDARY = 'legendary'


class Badge:
    """
    Badge template model defining available achievements.
    
    Attributes:
        _id: MongoDB ObjectId
        name: Badge name
        description: What the badge represents
        icon: Icon identifier or URL
        category: Badge category
        rarity: How rare the badge is
        points_value: Points awarded for earning
        criteria: Requirements to earn the badge
        is_active: Whether badge can be earned
        created_at: Creation timestamp
    """
    
    COLLECTION_NAME = 'badges'
    
    def __init__(
        self,
        name: str,
        description: str,
        icon: str,
        category: BadgeCategory,
        rarity: BadgeRarity = BadgeRarity.COMMON,
        points_value: int = 10,
        criteria: Optional[Dict] = None,
        is_active: bool = True,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.name = name
        self.description = description
        self.icon = icon
        self.category = category if isinstance(category, BadgeCategory) else BadgeCategory(category)
        self.rarity = rarity if isinstance(rarity, BadgeRarity) else BadgeRarity(rarity)
        self.points_value = points_value
        self.criteria = criteria or {}
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category.value,
            'rarity': self.rarity.value,
            'points_value': self.points_value,
            'criteria': self.criteria,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category.value,
            'rarity': self.rarity.value,
            'points_value': self.points_value,
            'criteria': self.criteria,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Badge':
        """Create from dictionary."""
        return cls(
            _id=data.get('_id'),
            name=data['name'],
            description=data['description'],
            icon=data['icon'],
            category=data['category'],
            rarity=data.get('rarity', BadgeRarity.COMMON),
            points_value=data.get('points_value', 10),
            criteria=data.get('criteria', {}),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )


class UserBadge:
    """
    Model for badges earned by users.
    
    Attributes:
        _id: MongoDB ObjectId
        user_id: Reference to user
        badge_id: Reference to badge template
        earned_at: When badge was earned
        progress: Progress towards badge (0-100)
        is_displayed: Whether user displays this badge
    """
    
    COLLECTION_NAME = 'user_badges'
    
    def __init__(
        self,
        user_id: ObjectId,
        badge_id: ObjectId,
        earned_at: Optional[datetime] = None,
        progress: int = 0,
        is_displayed: bool = True,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.badge_id = badge_id
        self.earned_at = earned_at
        self.progress = progress
        self.is_displayed = is_displayed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'badge_id': self.badge_id,
            'earned_at': self.earned_at,
            'progress': self.progress,
            'is_displayed': self.is_displayed
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'user_id': str(self.user_id),
            'badge_id': str(self.badge_id),
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'progress': self.progress,
            'is_displayed': self.is_displayed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserBadge':
        """Create from dictionary."""
        return cls(
            _id=data.get('_id'),
            user_id=data['user_id'],
            badge_id=data['badge_id'],
            earned_at=data.get('earned_at'),
            progress=data.get('progress', 0),
            is_displayed=data.get('is_displayed', True)
        )


# Predefined badge templates
DEFAULT_BADGES = [
    # Streak badges
    {
        'name': 'First Flame',
        'description': 'Complete your first day of learning',
        'icon': '🔥',
        'category': 'streak',
        'rarity': 'common',
        'points_value': 10,
        'criteria': {'streak_days': 1}
    },
    {
        'name': 'Week Warrior',
        'description': 'Maintain a 7-day learning streak',
        'icon': '⚡',
        'category': 'streak',
        'rarity': 'uncommon',
        'points_value': 50,
        'criteria': {'streak_days': 7}
    },
    {
        'name': 'Fortnight Fighter',
        'description': 'Maintain a 14-day learning streak',
        'icon': '💪',
        'category': 'streak',
        'rarity': 'rare',
        'points_value': 100,
        'criteria': {'streak_days': 14}
    },
    {
        'name': 'Monthly Master',
        'description': 'Maintain a 30-day learning streak',
        'icon': '🏆',
        'category': 'streak',
        'rarity': 'epic',
        'points_value': 250,
        'criteria': {'streak_days': 30}
    },
    {
        'name': 'Century Champion',
        'description': 'Maintain a 100-day learning streak',
        'icon': '👑',
        'category': 'streak',
        'rarity': 'legendary',
        'points_value': 1000,
        'criteria': {'streak_days': 100}
    },
    # Completion badges
    {
        'name': 'Quiz Starter',
        'description': 'Complete your first quiz',
        'icon': '📝',
        'category': 'completion',
        'rarity': 'common',
        'points_value': 10,
        'criteria': {'quizzes_completed': 1}
    },
    {
        'name': 'Quiz Expert',
        'description': 'Complete 50 quizzes',
        'icon': '🎯',
        'category': 'completion',
        'rarity': 'rare',
        'points_value': 150,
        'criteria': {'quizzes_completed': 50}
    },
    {
        'name': 'Course Completer',
        'description': 'Complete your first course',
        'icon': '📚',
        'category': 'completion',
        'rarity': 'uncommon',
        'points_value': 75,
        'criteria': {'courses_completed': 1}
    },
    # Performance badges
    {
        'name': 'Perfect Score',
        'description': 'Score 100% on any quiz',
        'icon': '💯',
        'category': 'performance',
        'rarity': 'uncommon',
        'points_value': 50,
        'criteria': {'perfect_quiz': True}
    },
    {
        'name': 'Speed Learner',
        'description': 'Complete a lesson in under 5 minutes',
        'icon': '⏱️',
        'category': 'performance',
        'rarity': 'uncommon',
        'points_value': 30,
        'criteria': {'fast_completion': True}
    },
    # Engagement badges
    {
        'name': 'Early Bird',
        'description': 'Complete an activity before 7 AM',
        'icon': '🌅',
        'category': 'engagement',
        'rarity': 'common',
        'points_value': 15,
        'criteria': {'early_activity': True}
    },
    {
        'name': 'Night Owl',
        'description': 'Complete an activity after 10 PM',
        'icon': '🦉',
        'category': 'engagement',
        'rarity': 'common',
        'points_value': 15,
        'criteria': {'late_activity': True}
    },
    {
        'name': 'Social Learner',
        'description': 'Post 10 discussion comments',
        'icon': '💬',
        'category': 'engagement',
        'rarity': 'uncommon',
        'points_value': 40,
        'criteria': {'discussion_posts': 10}
    }
]





