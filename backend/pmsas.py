"""
Progress Monitoring and Streak Analytics System (PMSAS) Module.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId

from database import get_database
from models.streak import Streak, EngagementLog
from models.badge import Badge, UserBadge, BadgeCategory, BadgeRarity, DEFAULT_BADGES
from models.leaderboard import UserPoints


class PMSASError(Exception):
    """Base exception for PMSAS-related errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PMSASService:
    """Main PMSAS service."""
    
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    def log_activity(self, user_id: str, activity_type: str, activity_id: Optional[str] = None,
                     duration_seconds: int = 0, points: int = 10, metadata: Optional[Dict] = None) -> Dict:
        """Log a learning activity and update streak."""
        if self.db is None:
            return {'streak': {'current_streak': 0}, 'new_badges': [], 'points_earned': points}
        
        user_oid = ObjectId(user_id)
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Create engagement log
        log = EngagementLog(
            user_id=user_oid,
            activity_type=activity_type,
            activity_id=ObjectId(activity_id) if activity_id else None,
            duration_seconds=duration_seconds,
            points_earned=points,
            metadata=metadata or {}
        )
        self.db.engagement_logs.insert_one(log.to_dict())
        
        # Get or create streak
        streak_data = self.db.streaks.find_one({'user_id': user_oid})
        if streak_data:
            streak = Streak.from_dict(streak_data)
        else:
            streak = Streak(user_id=user_oid)
        
        # Update streak logic
        last_activity = streak.last_activity_date
        if last_activity:
            last_day = last_activity.replace(hour=0, minute=0, second=0, microsecond=0)
            if last_day == today:
                pass  # Already active today
            elif last_day == today - timedelta(days=1):
                streak.current_streak += 1
            else:
                streak.current_streak = 1
                streak.streak_start_date = today
        else:
            streak.current_streak = 1
            streak.streak_start_date = today
        
        streak.last_activity_date = now
        streak.total_active_days += 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.updated_at = now
        
        self.db.streaks.update_one(
            {'user_id': user_oid},
            {'$set': streak.to_dict()},
            upsert=True
        )
        
        # Update points
        self.db.user_points.update_one(
            {'user_id': user_oid},
            {'$inc': {'total_points': points, 'weekly_points': points, 'monthly_points': points},
             '$set': {'updated_at': now}},
            upsert=True
        )
        
        return {
            'streak': streak.to_response_dict(),
            'new_badges': [],
            'points_earned': points
        }
    
    def get_user_streak(self, user_id: str) -> Dict:
        """Get user's current streak."""
        if self.db is None:
            return Streak(user_id=ObjectId(user_id)).to_response_dict()
        
        streak_data = self.db.streaks.find_one({'user_id': ObjectId(user_id)})
        if streak_data:
            return Streak.from_dict(streak_data).to_response_dict()
        return Streak(user_id=ObjectId(user_id)).to_response_dict()
    
    def get_all_badges(self, category: Optional[str] = None) -> List[Dict]:
        """Get all available badges."""
        if self.db is None:
            return []
        
        # Initialize badges if needed
        for badge_data in DEFAULT_BADGES:
            existing = self.db.badges.find_one({'name': badge_data['name']})
            if not existing:
                badge = Badge(
                    name=badge_data['name'],
                    description=badge_data['description'],
                    icon=badge_data['icon'],
                    category=BadgeCategory(badge_data['category']),
                    rarity=BadgeRarity(badge_data['rarity']),
                    points_value=badge_data['points_value'],
                    criteria=badge_data['criteria']
                )
                self.db.badges.insert_one(badge.to_dict())
        
        query = {'is_active': True}
        if category:
            query['category'] = category
        
        badges = self.db.badges.find(query)
        return [Badge.from_dict(b).to_response_dict() for b in badges]
    
    def get_user_badges(self, user_id: str) -> List[Dict]:
        """Get badges earned by a user."""
        if self.db is None:
            return []
        
        pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$lookup': {
                'from': 'badges',
                'localField': 'badge_id',
                'foreignField': '_id',
                'as': 'badge'
            }},
            {'$unwind': {'path': '$badge', 'preserveNullAndEmptyArrays': True}},
            {'$project': {
                'badge_id': 1,
                'earned_at': 1,
                'progress': 1,
                'name': '$badge.name',
                'description': '$badge.description',
                'icon': '$badge.icon',
                'category': '$badge.category',
                'rarity': '$badge.rarity',
                'points_value': '$badge.points_value'
            }}
        ]
        return list(self.db.user_badges.aggregate(pipeline))
    
    def get_leaderboard(self, leaderboard_type: str = 'streak', scope: str = 'global',
                        scope_id: Optional[str] = None, limit: int = 10, user_id: Optional[str] = None) -> Dict:
        """Get leaderboard data."""
        if self.db is None:
            return {'entries': [], 'total_participants': 0, 'user_rank': None, 'user_entry': None}
        
        if leaderboard_type == 'streak':
            pipeline = [
                {'$match': {'current_streak': {'$gt': 0}}},
                {'$sort': {'current_streak': -1}},
                {'$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user'
                }},
                {'$unwind': {'path': '$user', 'preserveNullAndEmptyArrays': True}},
                {'$project': {
                    'user_id': 1,
                    'score': '$current_streak',
                    'secondary_score': '$longest_streak',
                    'user_name': {'$concat': [{'$ifNull': ['$user.first_name', '']}, ' ', {'$ifNull': ['$user.last_name', '']}]}
                }}
            ]
            entries = list(self.db.streaks.aggregate(pipeline))
        else:
            entries = []
        
        for i, entry in enumerate(entries):
            entry['rank'] = i + 1
            entry['user_id'] = str(entry['user_id'])
            entry['_id'] = str(entry.get('_id', ''))
        
        user_rank = None
        user_entry = None
        if user_id:
            for entry in entries:
                if entry['user_id'] == user_id:
                    user_rank = entry['rank']
                    user_entry = entry
                    break
        
        return {
            'entries': entries[:limit],
            'total_participants': len(entries),
            'user_rank': user_rank,
            'user_entry': user_entry
        }
    
    def get_user_analytics(self, user_id: str) -> Dict:
        """Get user analytics."""
        if self.db is None:
            return {
                'streak': {'current': 0, 'longest': 0, 'total_active_days': 0, 'is_at_risk': False},
                'engagement': {'total_activities_30d': 0, 'total_time_seconds_30d': 0, 'activity_breakdown': {}, 'avg_daily_activities': 0},
                'points': {'total_points': 0},
                'badges': {'total_earned': 0},
                'predictions': {'engagement_level': 'new', 'consistency_score': 0, 'trend': 'neutral', 'risk_of_dropout': 'unknown', 'risk_score': 0, 'recommendations': ['Start learning!']}
            }
        
        user_oid = ObjectId(user_id)
        streak_data = self.db.streaks.find_one({'user_id': user_oid})
        points_data = self.db.user_points.find_one({'user_id': user_oid})
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        logs = list(self.db.engagement_logs.find({
            'user_id': user_oid,
            'created_at': {'$gte': thirty_days_ago}
        }))
        
        activity_counts = {}
        total_time = 0
        for log in logs:
            activity_type = log.get('activity_type', 'unknown')
            activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
            total_time += log.get('duration_seconds', 0)
        
        badges = list(self.db.user_badges.find({'user_id': user_oid, 'earned_at': {'$ne': None}}))
        
        # Simple predictions
        avg_daily = len(logs) / 30 if logs else 0
        if avg_daily >= 1:
            engagement = 'active'
        elif avg_daily >= 0.3:
            engagement = 'moderate'
        else:
            engagement = 'low'
        
        return {
            'streak': {
                'current': streak_data.get('current_streak', 0) if streak_data else 0,
                'longest': streak_data.get('longest_streak', 0) if streak_data else 0,
                'total_active_days': streak_data.get('total_active_days', 0) if streak_data else 0,
                'is_at_risk': streak_data.get('is_at_risk', False) if streak_data else False
            },
            'engagement': {
                'total_activities_30d': len(logs),
                'total_time_seconds_30d': total_time,
                'activity_breakdown': activity_counts,
                'avg_daily_activities': round(avg_daily, 2)
            },
            'points': {
                'total_points': points_data.get('total_points', 0) if points_data else 0,
                'weekly_points': points_data.get('weekly_points', 0) if points_data else 0,
                'monthly_points': points_data.get('monthly_points', 0) if points_data else 0
            },
            'badges': {'total_earned': len(badges)},
            'predictions': {
                'engagement_level': engagement,
                'consistency_score': min(100, (streak_data.get('current_streak', 0) if streak_data else 0) * 10),
                'trend': 'stable',
                'risk_of_dropout': 'low' if avg_daily >= 0.5 else 'medium',
                'risk_score': 30 if avg_daily < 0.5 else 10,
                'recommendations': ['Keep up the great work!'] if avg_daily >= 1 else ['Try to learn something every day!']
            }
        }
    
    def get_teacher_dashboard(self, class_id: Optional[str] = None) -> Dict:
        """Get teacher dashboard."""
        if self.db is None:
            return {'total_students': 0, 'active_today': 0, 'at_risk_count': 0, 'avg_streak': 0, 'streak_distribution': {}, 'top_performers': [], 'at_risk_students': []}
        
        streaks = list(self.db.streaks.find({}))
        if not streaks:
            return {'total_students': 0, 'active_today': 0, 'active_today_percent': 0, 'at_risk_count': 0, 'avg_streak': 0, 'streak_distribution': {'0': 0, '1-7': 0, '8-14': 0, '15-30': 0, '30+': 0}, 'top_performers': [], 'at_risk_students': []}
        
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_today = sum(1 for s in streaks if s.get('last_activity_date') and s['last_activity_date'].replace(hour=0, minute=0, second=0, microsecond=0) == today)
        at_risk = [s for s in streaks if s.get('is_at_risk')]
        avg_streak = sum(s.get('current_streak', 0) for s in streaks) / len(streaks)
        
        distribution = {'0': 0, '1-7': 0, '8-14': 0, '15-30': 0, '30+': 0}
        for s in streaks:
            cs = s.get('current_streak', 0)
            if cs == 0: distribution['0'] += 1
            elif cs <= 7: distribution['1-7'] += 1
            elif cs <= 14: distribution['8-14'] += 1
            elif cs <= 30: distribution['15-30'] += 1
            else: distribution['30+'] += 1
        
        top = sorted(streaks, key=lambda x: x.get('current_streak', 0), reverse=True)[:5]
        
        return {
            'total_students': len(streaks),
            'active_today': active_today,
            'active_today_percent': round(active_today / len(streaks) * 100, 1),
            'at_risk_count': len(at_risk),
            'avg_streak': round(avg_streak, 1),
            'streak_distribution': distribution,
            'top_performers': [{'user_id': str(s['user_id']), 'current_streak': s.get('current_streak', 0), 'longest_streak': s.get('longest_streak', 0)} for s in top],
            'at_risk_students': [{'user_id': str(s['user_id']), 'current_streak': s.get('current_streak', 0), 'last_activity': s.get('last_activity_date').isoformat() if s.get('last_activity_date') else None} for s in at_risk]
        }
    
    def get_at_risk_students(self) -> List[Dict]:
        """Get at-risk students."""
        if self.db is None:
            return []
        
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        
        at_risk = list(self.db.streaks.find({
            'current_streak': {'$gt': 0},
            'last_activity_date': {'$gte': yesterday, '$lt': today}
        }))
        
        return [{'user_id': str(s['user_id']), 'current_streak': s.get('current_streak', 0), 'last_activity': s.get('last_activity_date').isoformat() if s.get('last_activity_date') else None} for s in at_risk]
    
    def get_user_points(self, user_id: str) -> Dict:
        """Get user points."""
        if self.db is None:
            return {'user_id': user_id, 'total_points': 0, 'weekly_points': 0, 'monthly_points': 0, 'level': 1, 'points_to_next_level': 100, 'level_progress': 0}
        
        points_data = self.db.user_points.find_one({'user_id': ObjectId(user_id)})
        if points_data:
            pts = UserPoints.from_dict(points_data)
            return pts.to_response_dict()
        return {'user_id': user_id, 'total_points': 0, 'weekly_points': 0, 'monthly_points': 0, 'level': 1, 'points_to_next_level': 100, 'level_progress': 0}


# Create singleton instance
pmsas_service = PMSASService()

