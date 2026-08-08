"""
Authentication Routes
Server-side role enforcement and RBAC
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from db import db
import jwt
import os
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'error': 'Invalid token format'}, 401
        
        if not token:
            return {'error': 'Token is missing'}, 401
        
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY', 'dev-secret'), algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user = db.get_user(current_user_id)
            if not current_user:
                return {'error': 'User not found'}, 401
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}, 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def role_required(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(current_user, *args, **kwargs):
            # Server-side role enforcement - NEVER trust client
            if current_user['role'] != required_role:
                return {'error': f'This action requires {required_role} role'}, 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)

def teacher_required(f):
    """Decorator to require teacher role"""
    return role_required('teacher')(f)

def student_required(f):
    """Decorator to require student role"""
    return role_required('student')(f)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return {'error': 'Missing required fields: email, password, name'}, 400
    
    # Check if user already exists
    existing_user = db.get_user_by_email(data['email'])
    if existing_user:
        return {'error': 'Email already registered'}, 409
    
    # Server-side role enforcement - NEVER trust client role input
    # Default to student, only admin can create teachers
    role = 'student'
    
    try:
        user = db.create_user(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            role=role
        )
        
        return {
            'message': 'User registered successfully',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role']
            }
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return {'error': 'Missing email or password'}, 400
    
    user = db.get_user_by_email(data['email'])
    if not user:
        return {'error': 'Invalid credentials'}, 401
    
    # In production, verify password hash
    # For now, simple comparison (CHANGE THIS IN PRODUCTION)
    if user.get('password') != data['password']:
        return {'error': 'Invalid credentials'}, 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, os.getenv('SECRET_KEY', 'dev-secret'), algorithm='HS256')
    
    return {
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role'],
            'teacher_approval_status': user.get('teacher_approval_status')
        }
    }, 200

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    return {
        'user': {
            'id': current_user['id'],
            'email': current_user['email'],
            'name': current_user['name'],
            'role': current_user['role'],
            'teacher_approval_status': current_user.get('teacher_approval_status')
        }
    }, 200

@auth_bp.route('/request-teacher-role', methods=['POST'])
@token_required
def request_teacher_role(current_user):
    """Request teacher role (requires admin approval)"""
    if current_user['role'] != 'student':
        return {'error': 'Only students can request teacher role'}, 400
    
    try:
        db.update_user(current_user['id'], {
            'role': 'teacher',
            'teacher_approval_status': 'pending'
        })
        
        return {
            'message': 'Teacher role request submitted. Awaiting admin approval.'
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@auth_bp.route('/approve-teacher/<int:user_id>', methods=['POST'])
@admin_required
def approve_teacher(current_user, user_id):
    """Admin: Approve teacher role request"""
    try:
        user = db.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        if user['role'] != 'teacher' or user['teacher_approval_status'] != 'pending':
            return {'error': 'User is not pending teacher approval'}, 400
        
        db.update_user(user_id, {
            'teacher_approval_status': 'approved'
        })
        
        return {
            'message': f'Teacher role approved for {user["name"]}'
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@auth_bp.route('/reject-teacher/<int:user_id>', methods=['POST'])
@admin_required
def reject_teacher(current_user, user_id):
    """Admin: Reject teacher role request"""
    try:
        user = db.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        
        if user['role'] != 'teacher' or user['teacher_approval_status'] != 'pending':
            return {'error': 'User is not pending teacher approval'}, 400
        
        db.update_user(user_id, {
            'role': 'student',
            'teacher_approval_status': 'rejected'
        })
        
        return {
            'message': f'Teacher role rejected for {user["name"]}'
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@auth_bp.route('/pending-teachers', methods=['GET'])
@admin_required
def get_pending_teachers(current_user):
    """Admin: Get list of pending teacher approvals"""
    try:
        # This would require a query method in db.py
        # For now, return placeholder
        return {
            'pending_teachers': []
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500
