"""PMSAS Routes - Progress Monitoring and Streak Analytics System API"""

from functools import wraps
from flask import Blueprint, request, jsonify, g
from pmsas import pmsas_service, PMSASError
from accounts import account_service, AccountError

pmsas_bp = Blueprint('pmsas', __name__, url_prefix='/api/pmsas')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Bearer '):
            return jsonify({'error': 'Token required'}), 401
        try:
            payload = account_service.verify_token(auth.split(' ')[1])
            g.user_id = payload['user_id']
            g.user_role = payload['role']
        except AccountError as e:
            return jsonify({'error': e.message}), e.status_code
        return f(*args, **kwargs)
    return decorated

def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user_role not in ['teacher', 'admin']:
            return jsonify({'error': 'Access denied'}), 403
        return f(*args, **kwargs)
    return decorated

@pmsas_bp.route('/activity', methods=['POST'])
@token_required
def log_activity():
    data = request.get_json() or {}
    if 'activity_type' not in data:
        return jsonify({'error': 'activity_type required'}), 400
    try:
        result = pmsas_service.log_activity(
            user_id=g.user_id,
            activity_type=data['activity_type'],
            activity_id=data.get('activity_id'),
            duration_seconds=data.get('duration_seconds', 0),
            points=data.get('points', 10),
            metadata=data.get('metadata')
        )
        return jsonify(result), 201
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/streak', methods=['GET'])
@token_required
def get_streak():
    try:
        return jsonify({'streak': pmsas_service.get_user_streak(g.user_id)}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/badges', methods=['GET'])
@token_required
def get_badges():
    try:
        return jsonify({'badges': pmsas_service.get_all_badges(request.args.get('category'))}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/badges/me', methods=['GET'])
@token_required
def get_my_badges():
    try:
        return jsonify({'badges': pmsas_service.get_user_badges(g.user_id)}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/leaderboard', methods=['GET'])
@token_required
def get_leaderboard():
    try:
        lb = pmsas_service.get_leaderboard(
            leaderboard_type=request.args.get('type', 'streak'),
            limit=int(request.args.get('limit', 10)),
            user_id=g.user_id
        )
        return jsonify({'leaderboard': lb}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/points', methods=['GET'])
@token_required
def get_points():
    try:
        return jsonify({'points': pmsas_service.get_user_points(g.user_id)}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/analytics/me', methods=['GET'])
@token_required
def get_analytics():
    try:
        return jsonify({'analytics': pmsas_service.get_user_analytics(g.user_id)}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/dashboard/teacher', methods=['GET'])
@token_required
@teacher_required
def get_teacher_dashboard():
    try:
        return jsonify({'dashboard': pmsas_service.get_teacher_dashboard(request.args.get('class_id'))}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/dashboard/at-risk', methods=['GET'])
@token_required
@teacher_required
def get_at_risk():
    try:
        return jsonify({'at_risk_students': pmsas_service.get_at_risk_students()}), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code

@pmsas_bp.route('/summary', methods=['GET'])
@token_required
def get_summary():
    try:
        streak = pmsas_service.get_user_streak(g.user_id)
        points = pmsas_service.get_user_points(g.user_id)
        badges = pmsas_service.get_user_badges(g.user_id)
        earned = [b for b in badges if b.get('earned_at')]
        return jsonify({
            'summary': {
                'current_streak': streak.get('current_streak', 0),
                'longest_streak': streak.get('longest_streak', 0),
                'is_at_risk': streak.get('is_at_risk', False),
                'total_points': points.get('total_points', 0),
                'level': points.get('level', 1),
                'level_progress': points.get('level_progress', 0),
                'badges_earned': len(earned),
                'total_active_days': streak.get('total_active_days', 0)
            }
        }), 200
    except PMSASError as e:
        return jsonify({'error': e.message}), e.status_code





