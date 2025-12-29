"""
Account Management Module.

This module handles all account-related operations including:
- User registration
- User authentication
- Profile management
- Account updates
- Password management

Follows the Single Responsibility Principle by keeping all account
logic separate from the main application.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
import bcrypt
import jwt
from email_validator import validate_email, EmailNotValidError

from database import get_database
from models import User, UserRole
from config import get_config


class AccountError(Exception):
    """Base exception for account-related errors."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AccountService:
    """
    Service class for account management operations.
    
    Implements business logic for user account operations,
    following the Service Layer pattern.
    """
    
    def __init__(self):
        self._db = None
        self._users_collection = None
        self.config = get_config()
    
    @property
    def db(self):
        """Lazy load database connection."""
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def users_collection(self):
        """Lazy load users collection."""
        if self._users_collection is None and self.db is not None:
            self._users_collection = self.db.users
        return self._users_collection
    
    # ==================== Password Utilities ====================
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    # ==================== Token Management ====================
    
    def _generate_token(self, user: User) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user: User instance
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': str(user._id),
            'email': user.email,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=self.config.JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, self.config.JWT_SECRET_KEY, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AccountError('Token has expired', 401)
        except jwt.InvalidTokenError:
            raise AccountError('Invalid token', 401)
    
    # ==================== Validation ====================
    
    def _validate_email(self, email: str) -> str:
        """
        Validate and normalize an email address.
        
        Args:
            email: Email address to validate
            
        Returns:
            Normalized email address
            
        Raises:
            AccountError: If email is invalid
        """
        try:
            # In development, use check_deliverability=False to allow test domains
            valid = validate_email(email, check_deliverability=False)
            return valid.email
        except EmailNotValidError as e:
            raise AccountError(f'Invalid email address: {str(e)}')
    
    def _validate_password(self, password: str) -> None:
        """
        Validate password meets requirements.
        
        Args:
            password: Password to validate
            
        Raises:
            AccountError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise AccountError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in password):
            raise AccountError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in password):
            raise AccountError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in password):
            raise AccountError('Password must contain at least one digit')
    
    def _validate_role(self, role: str) -> UserRole:
        """
        Validate and convert role string to UserRole enum.
        
        Args:
            role: Role string
            
        Returns:
            UserRole enum value
            
        Raises:
            AccountError: If role is invalid
        """
        try:
            return UserRole(role.lower())
        except ValueError:
            valid_roles = [r.value for r in UserRole]
            raise AccountError(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
    
    # ==================== CRUD Operations ====================
    
    def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = 'student'
    ) -> Tuple[User, str]:
        """
        Register a new user account.
        
        Args:
            email: User's email address
            password: User's password
            first_name: User's first name
            last_name: User's last name
            role: User's role (default: student)
            
        Returns:
            Tuple of (User instance, JWT token)
            
        Raises:
            AccountError: If registration fails
        """
        # Validate inputs
        email = self._validate_email(email)
        self._validate_password(password)
        user_role = self._validate_role(role)
        
        if not first_name or not first_name.strip():
            raise AccountError('First name is required')
        if not last_name or not last_name.strip():
            raise AccountError('Last name is required')
        
        # Check database connection
        if self.users_collection is None:
            raise AccountError('Database connection failed. Please try again later.', 503)
        
        # Check if email already exists
        if self.users_collection.find_one({'email': email}):
            raise AccountError('An account with this email already exists')
        
        # Create user
        user = User(
            email=email,
            password_hash=self._hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=user_role
        )
        
        # Insert into database
        self.users_collection.insert_one(user.to_dict(include_password=True))
        
        # Generate token
        token = self._generate_token(user)
        
        return user, token
    
    def login(self, email: str, password: str) -> Tuple[User, str]:
        """
        Authenticate a user and return a token.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (User instance, JWT token)
            
        Raises:
            AccountError: If authentication fails
        """
        # Check database connection
        if self.users_collection is None:
            raise AccountError('Database connection failed. Please try again later.', 503)
        
        email = email.lower().strip()
        
        # Find user
        user_data = self.users_collection.find_one({'email': email})
        if not user_data:
            raise AccountError('No account found with this email address', 401)
        
        user = User.from_dict(user_data)
        
        # Check if account is active
        if not user.is_active:
            raise AccountError('Account is deactivated. Please contact support.', 403)
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            raise AccountError('Incorrect password. Please try again.', 401)
        
        # Generate token
        token = self._generate_token(user)
        
        return user, token
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: User's ObjectId as string
            
        Returns:
            User instance if found, None otherwise
        """
        try:
            user_data = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User.from_dict(user_data)
            return None
        except Exception:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email.
        
        Args:
            email: User's email address
            
        Returns:
            User instance if found, None otherwise
        """
        user_data = self.users_collection.find_one({'email': email.lower().strip()})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_all_users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[User], int]:
        """
        Get all users with optional filtering and pagination.
        
        Args:
            role: Filter by role
            is_active: Filter by active status
            page: Page number (1-indexed)
            per_page: Number of users per page
            
        Returns:
            Tuple of (list of Users, total count)
        """
        # Build query
        query = {}
        if role:
            query['role'] = role.lower()
        if is_active is not None:
            query['is_active'] = is_active
        
        # Get total count
        total = self.users_collection.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * per_page
        cursor = self.users_collection.find(query).skip(skip).limit(per_page)
        
        users = [User.from_dict(data) for data in cursor]
        
        return users, total
    
    def update_profile(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        bio: Optional[str] = None,
        profile_image: Optional[str] = None
    ) -> User:
        """
        Update a user's profile information.
        
        Args:
            user_id: User's ObjectId as string
            first_name: New first name
            last_name: New last name
            phone: New phone number
            bio: New biography
            profile_image: New profile image URL
            
        Returns:
            Updated User instance
            
        Raises:
            AccountError: If update fails
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise AccountError('User not found', 404)
        
        # Build update document
        update_data = {'updated_at': datetime.utcnow()}
        
        if first_name is not None:
            if not first_name.strip():
                raise AccountError('First name cannot be empty')
            update_data['first_name'] = first_name.strip()
        
        if last_name is not None:
            if not last_name.strip():
                raise AccountError('Last name cannot be empty')
            update_data['last_name'] = last_name.strip()
        
        if phone is not None:
            update_data['phone'] = phone.strip() if phone else None
        
        if bio is not None:
            update_data['bio'] = bio.strip() if bio else None
        
        if profile_image is not None:
            update_data['profile_image'] = profile_image.strip() if profile_image else None
        
        # Update in database
        self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        # Return updated user
        return self.get_user_by_id(user_id)
    
    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change a user's password.
        
        Args:
            user_id: User's ObjectId as string
            current_password: Current password for verification
            new_password: New password
            
        Raises:
            AccountError: If password change fails
        """
        user_data = self.users_collection.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            raise AccountError('User not found', 404)
        
        user = User.from_dict(user_data)
        
        # Verify current password
        if not self._verify_password(current_password, user.password_hash):
            raise AccountError('Current password is incorrect', 401)
        
        # Validate new password
        self._validate_password(new_password)
        
        # Update password
        self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'password_hash': self._hash_password(new_password),
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    def update_email(self, user_id: str, new_email: str, password: str) -> User:
        """
        Update a user's email address.
        
        Args:
            user_id: User's ObjectId as string
            new_email: New email address
            password: Password for verification
            
        Returns:
            Updated User instance
            
        Raises:
            AccountError: If email update fails
        """
        user_data = self.users_collection.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            raise AccountError('User not found', 404)
        
        user = User.from_dict(user_data)
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            raise AccountError('Password is incorrect', 401)
        
        # Validate new email
        new_email = self._validate_email(new_email)
        
        # Check if email is already in use
        existing = self.users_collection.find_one({'email': new_email})
        if existing and str(existing['_id']) != user_id:
            raise AccountError('This email is already in use')
        
        # Update email
        self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'email': new_email,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return self.get_user_by_id(user_id)
    
    def deactivate_account(self, user_id: str) -> None:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's ObjectId as string
            
        Raises:
            AccountError: If deactivation fails
        """
        result = self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'is_active': False,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise AccountError('User not found', 404)
    
    def activate_account(self, user_id: str) -> None:
        """
        Activate a user account.
        
        Args:
            user_id: User's ObjectId as string
            
        Raises:
            AccountError: If activation fails
        """
        result = self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'is_active': True,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise AccountError('User not found', 404)
    
    def update_role(self, user_id: str, new_role: str, admin_id: str) -> User:
        """
        Update a user's role (admin only).
        
        Args:
            user_id: Target user's ObjectId as string
            new_role: New role to assign
            admin_id: Admin user's ObjectId for authorization
            
        Returns:
            Updated User instance
            
        Raises:
            AccountError: If role update fails
        """
        # Verify admin
        admin = self.get_user_by_id(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise AccountError('Only administrators can change user roles', 403)
        
        # Validate role
        role = self._validate_role(new_role)
        
        # Update role
        result = self.users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'role': role.value,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise AccountError('User not found', 404)
        
        return self.get_user_by_id(user_id)
    
    def delete_account(self, user_id: str) -> None:
        """
        Permanently delete a user account.
        
        Args:
            user_id: User's ObjectId as string
            
        Raises:
            AccountError: If deletion fails
        """
        result = self.users_collection.delete_one({'_id': ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise AccountError('User not found', 404)


# Create a singleton instance
account_service = AccountService()


