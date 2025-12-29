"""
User model module.
Defines the User model and related enums.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId


class UserRole(str, Enum):
    """Enumeration of user roles in the system."""
    
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'


class User:
    """
    User model representing a user in the e-learning system.
    
    Attributes:
        _id: MongoDB ObjectId
        email: User's email address (unique)
        password_hash: Hashed password
        first_name: User's first name
        last_name: User's last name
        role: User's role (admin, teacher, student)
        profile_image: URL to profile image
        phone: Phone number
        bio: User biography
        is_active: Whether the account is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    COLLECTION_NAME = 'users'
    
    def __init__(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.STUDENT,
        profile_image: Optional[str] = None,
        phone: Optional[str] = None,
        bio: Optional[str] = None,
        is_active: bool = True,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.email = email.lower().strip()
        self.password_hash = password_hash
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.profile_image = profile_image
        self.phone = phone
        self.bio = bio
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """
        Convert user to dictionary representation.
        
        Args:
            include_password: Whether to include password hash
            
        Returns:
            Dictionary representation of the user
        """
        data = {
            '_id': self._id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role.value,
            'profile_image': self.profile_image,
            'phone': self.phone,
            'bio': self.bio,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
            
        return data
    
    def to_response_dict(self) -> Dict[str, Any]:
        """
        Convert user to API response dictionary.
        Excludes sensitive data and converts ObjectId to string.
        
        Returns:
            Dictionary safe for API response
        """
        return {
            'id': str(self._id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role.value,
            'profile_image': self.profile_image,
            'phone': self.phone,
            'bio': self.bio,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User instance from a dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            User instance
        """
        return cls(
            _id=data.get('_id'),
            email=data['email'],
            password_hash=data['password_hash'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', UserRole.STUDENT),
            profile_image=data.get('profile_image'),
            phone=data.get('phone'),
            bio=data.get('bio'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )






