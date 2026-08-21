"""
Courses Routes
Course and class management with teacher authorization
"""

import secrets
import string

from flask import Blueprint, request

from backend.api.auth import teacher_required, token_required
from backend.db import db

courses_bp = Blueprint('courses', __name__)

def generate_enrollment_code(length=8):
    """Generate a random enrollment code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

# ============ COURSE ENDPOINTS ============

@courses_bp.route('', methods=['GET'])
@token_required
def list_courses(current_user):
    """List all courses"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        courses = db.get_courses(limit=limit, offset=offset)
        
        return {
            'courses': courses,
            'total': len(courses),
            'limit': limit,
            'offset': offset
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('', methods=['POST'])
@teacher_required
def create_course(current_user):
    """Create a new course (teacher only)"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return {'error': 'Missing required field: title'}, 400
    
    try:
        course = db.create_course(
            title=data['title'],
            description=data.get('description', ''),
            created_by=current_user['id']
        )
        
        return {
            'message': 'Course created successfully',
            'course': course
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
@token_required
def get_course(current_user, course_id):
    """Get course details"""
    try:
        course = db.get_course(course_id)
        
        if not course:
            return {'error': 'Course not found'}, 404
        
        return {'course': course}, 200
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@teacher_required
def update_course(current_user, course_id):
    """Update course (teacher only)"""
    course = db.get_course(course_id)
    
    if not course:
        return {'error': 'Course not found'}, 404
    
    # Check authorization - only creator can update
    if course['created_by'] != current_user['id']:
        return {'error': 'You do not have permission to update this course'}, 403
    
    data = request.get_json()
    
    try:
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        
        if not update_data:
            return {'error': 'No fields to update'}, 400
        
        updated_course = db.client.table('courses').update(update_data).eq('id', course_id).execute()
        
        return {
            'message': 'Course updated successfully',
            'course': updated_course.data[0] if updated_course.data else None
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@teacher_required
def delete_course(current_user, course_id):
    """Delete course (teacher only)"""
    course = db.get_course(course_id)
    
    if not course:
        return {'error': 'Course not found'}, 404
    
    # Check authorization
    if course['created_by'] != current_user['id']:
        return {'error': 'You do not have permission to delete this course'}, 403
    
    try:
        db.client.table('courses').delete().eq('id', course_id).execute()
        
        return {'message': 'Course deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# ============ CLASS ENDPOINTS ============

@courses_bp.route('/<int:course_id>/classes', methods=['GET'])
@token_required
def list_classes(current_user, course_id):
    """List classes for a course"""
    try:
        classes = db.client.table('classes').select('*').eq('course_id', course_id).execute()
        
        return {
            'classes': classes.data,
            'total': len(classes.data)
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/<int:course_id>/classes', methods=['POST'])
@teacher_required
def create_class(current_user, course_id):
    """Create a new class (teacher only)"""
    course = db.get_course(course_id)
    
    if not course:
        return {'error': 'Course not found'}, 404
    
    data = request.get_json()
    
    if not data or not data.get('name'):
        return {'error': 'Missing required field: name'}, 400
    
    try:
        # Generate unique enrollment code
        enrollment_code = generate_enrollment_code()
        
        class_obj = db.create_class(
            course_id=course_id,
            teacher_id=current_user['id'],
            name=data['name'],
            enrollment_code=enrollment_code
        )
        
        return {
            'message': 'Class created successfully',
            'class': class_obj
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/classes/<int:class_id>', methods=['GET'])
@token_required
def get_class(current_user, class_id):
    """Get class details"""
    try:
        class_obj = db.get_class(class_id)
        
        if not class_obj:
            return {'error': 'Class not found'}, 404
        
        return {'class': class_obj}, 200
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/classes/<int:class_id>/enroll', methods=['POST'])
@token_required
def enroll_in_class(current_user, class_id):
    """Enroll student in a class using enrollment code"""
    if current_user['role'] != 'student':
        return {'error': 'Only students can enroll in classes'}, 400
    
    data = request.get_json()
    
    if not data or not data.get('enrollment_code'):
        return {'error': 'Missing required field: enrollment_code'}, 400
    
    try:
        class_obj = db.get_class(class_id)
        
        if not class_obj:
            return {'error': 'Class not found'}, 404
        
        if class_obj['enrollment_code'] != data['enrollment_code']:
            return {'error': 'Invalid enrollment code'}, 400
        
        # Check if already enrolled
        existing = db.client.table('enrollments').select('*').eq('class_id', class_id).eq('user_id', current_user['id']).execute()
        
        if existing.data:
            return {'error': 'Already enrolled in this class'}, 409
        
        # Create enrollment
        enrollment = db.client.table('enrollments').insert({
            'class_id': class_id,
            'user_id': current_user['id'],
            'enrollment_role': 'student'
        }).execute()
        
        return {
            'message': 'Successfully enrolled in class',
            'enrollment': enrollment.data[0] if enrollment.data else None
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/classes/<int:class_id>/students', methods=['GET'])
@teacher_required
def get_class_students(current_user, class_id):
    """Get students in a class (teacher only)"""
    try:
        class_obj = db.get_class(class_id)
        
        if not class_obj:
            return {'error': 'Class not found'}, 404
        
        # Check authorization
        if class_obj['teacher_id'] != current_user['id']:
            return {'error': 'You do not have permission to view this class'}, 403
        
        # Get enrollments
        enrollments = db.client.table('enrollments').select('*').eq('class_id', class_id).eq('enrollment_role', 'student').execute()
        
        students = []
        for enrollment in enrollments.data:
            student = db.get_user(enrollment['user_id'])
            if student:
                students.append({
                    'id': student['id'],
                    'name': student['name'],
                    'email': student['email'],
                    'joined_at': enrollment['joined_at']
                })
        
        return {
            'students': students,
            'total': len(students)
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@courses_bp.route('/teacher/classes', methods=['GET'])
@teacher_required
def get_teacher_classes(current_user):
    """Get all classes taught by current teacher"""
    try:
        classes = db.get_teacher_classes(current_user['id'])
        
        return {
            'classes': classes,
            'total': len(classes)
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500
