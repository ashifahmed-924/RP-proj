"""
Account Routes Module.

Defines REST API endpoints for account management.
All routes are prefixed with /api/accounts.
"""

from functools import wraps
from flask import Blueprint, request, jsonify, g

from accounts import account_service, AccountError


account_bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')


# ==================== Middleware ====================

def token_required(f):
    """
    Decorator to require valid JWT token for protected routes.
    Adds user info to Flask's g object.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is required'}), 401
        
        try:
            payload = account_service.verify_token(token)
            g.user_id = payload['user_id']
            g.user_role = payload['role']
            g.user_email = payload['email']
        except AccountError as e:
            return jsonify({'error': e.message}), e.status_code
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f):
    """
    Decorator to require admin role for protected routes.
    Must be used after token_required.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user_role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated


# ==================== Public Routes ====================

@account_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Request Body:
        - email: string (required)
        - password: string (required)
        - first_name: string (required)
        - last_name: string (required)
        - role: string (optional, default: student)
    
    Returns:
        201: User created successfully
        400: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        user, token = account_service.register(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'student')
        )
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_response_dict(),
            'token': token
        }), 201
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user.
    
    Request Body:
        - email: string (required)
        - password: string (required)
    
    Returns:
        200: Login successful
        401: Invalid credentials
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        user, token = account_service.login(
            email=data['email'],
            password=data['password']
        )
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_response_dict(),
            'token': token
        }), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


# ==================== Protected Routes ====================

@account_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """
    Get the current authenticated user's profile.
    
    Returns:
        200: User profile
        404: User not found
    """
    try:
        user = account_service.get_user_by_id(g.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_response_dict()}), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/me', methods=['PUT'])
@token_required
def update_current_user():
    """
    Update the current user's profile.
    
    Request Body (all optional):
        - first_name: string
        - last_name: string
        - phone: string
        - bio: string
        - profile_image: string (URL)
    
    Returns:
        200: Profile updated
        400: Validation error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    try:
        user = account_service.update_profile(
            user_id=g.user_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            bio=data.get('bio'),
            profile_image=data.get('profile_image')
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_response_dict()
        }), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/me/password', methods=['PUT'])
@token_required
def change_password():
    """
    Change the current user's password.
    
    Request Body:
        - current_password: string (required)
        - new_password: string (required)
    
    Returns:
        200: Password changed
        401: Invalid current password
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if 'current_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    try:
        account_service.change_password(
            user_id=g.user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/me/email', methods=['PUT'])
@token_required
def update_email():
    """
    Update the current user's email address.
    
    Request Body:
        - new_email: string (required)
        - password: string (required, for verification)
    
    Returns:
        200: Email updated
        401: Invalid password
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if 'new_email' not in data or 'password' not in data:
        return jsonify({'error': 'New email and password are required'}), 400
    
    try:
        user = account_service.update_email(
            user_id=g.user_id,
            new_email=data['new_email'],
            password=data['password']
        )
        
        return jsonify({
            'message': 'Email updated successfully',
            'user': user.to_response_dict()
        }), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/me/deactivate', methods=['POST'])
@token_required
def deactivate_own_account():
    """
    Deactivate the current user's account.
    
    Returns:
        200: Account deactivated
    """
    try:
        account_service.deactivate_account(g.user_id)
        return jsonify({'message': 'Account deactivated successfully'}), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


# ==================== Admin Routes ====================

@account_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_all_users():
    """
    Get all users (admin only).
    
    Query Parameters:
        - role: Filter by role (admin, teacher, student)
        - is_active: Filter by active status (true/false)
        - page: Page number (default: 1)
        - per_page: Users per page (default: 20)
    
    Returns:
        200: List of users with pagination info
    """
    role = request.args.get('role')
    is_active = request.args.get('is_active')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Convert is_active to boolean if provided
    if is_active is not None:
        is_active = is_active.lower() == 'true'
    
    try:
        users, total = account_service.get_all_users(
            role=role,
            is_active=is_active,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'users': [user.to_response_dict() for user in users],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/users/<user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(user_id):
    """
    Get a specific user by ID (admin only).
    
    Returns:
        200: User profile
        404: User not found
    """
    try:
        user = account_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_response_dict()}), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/users/<user_id>/role', methods=['PUT'])
@token_required
@admin_required
def update_user_role(user_id):
    """
    Update a user's role (admin only).
    
    Request Body:
        - role: string (required, one of: admin, teacher, student)
    
    Returns:
        200: Role updated
        400: Invalid role
        404: User not found
    """
    data = request.get_json()
    
    if not data or 'role' not in data:
        return jsonify({'error': 'Role is required'}), 400
    
    try:
        user = account_service.update_role(
            user_id=user_id,
            new_role=data['role'],
            admin_id=g.user_id
        )
        
        return jsonify({
            'message': 'Role updated successfully',
            'user': user.to_response_dict()
        }), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/users/<user_id>/activate', methods=['POST'])
@token_required
@admin_required
def activate_user(user_id):
    """
    Activate a user account (admin only).
    
    Returns:
        200: Account activated
        404: User not found
    """
    try:
        account_service.activate_account(user_id)
        return jsonify({'message': 'Account activated successfully'}), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/users/<user_id>/deactivate', methods=['POST'])
@token_required
@admin_required
def deactivate_user(user_id):
    """
    Deactivate a user account (admin only).
    
    Returns:
        200: Account deactivated
        404: User not found
    """
    try:
        account_service.deactivate_account(user_id)
        return jsonify({'message': 'Account deactivated successfully'}), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code


@account_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(user_id):
    """
    Delete a user account (admin only).
    
    Returns:
        200: Account deleted
        404: User not found
    """
    try:
        account_service.delete_account(user_id)
        return jsonify({'message': 'Account deleted successfully'}), 200
        
    except AccountError as e:
        return jsonify({'error': e.message}), e.status_code






