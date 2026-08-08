"""
Problems Routes
Problem bank management with test cases and hints
"""

from flask import Blueprint, request, jsonify
from routes.auth import token_required, teacher_required
from db import db
import hashlib

problems_bp = Blueprint('problems', __name__)

# ============ PROBLEM ENDPOINTS ============

@problems_bp.route('', methods=['GET'])
@token_required
def list_problems(current_user):
    """List all problems"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        difficulty = request.args.get('difficulty')
        
        problems = db.get_problems(limit=limit, offset=offset)
        
        if difficulty:
            problems = [p for p in problems if p.get('difficulty') == difficulty]
        
        return {
            'problems': problems,
            'total': len(problems),
            'limit': limit,
            'offset': offset
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@problems_bp.route('', methods=['POST'])
@teacher_required
def create_problem(current_user):
    """Create a new problem (teacher only)"""
    data = request.get_json()
    
    required_fields = ['title', 'description', 'difficulty', 'starter_code']
    if not data or not all(field in data for field in required_fields):
        return {'error': f'Missing required fields: {required_fields}'}, 400
    
    if data['difficulty'] not in ['easy', 'medium', 'hard']:
        return {'error': 'Difficulty must be easy, medium, or hard'}, 400
    
    try:
        problem = db.create_problem(
            title=data['title'],
            description=data['description'],
            difficulty=data['difficulty'],
            starter_code=data['starter_code'],
            created_by=current_user['id'],
            language=data.get('language', 'python')
        )
        
        # Create initial version
        content_hash = hashlib.sha256(
            (data['starter_code'] + data['description']).encode()
        ).hexdigest()
        
        db.client.table('problem_versions').insert({
            'problem_id': problem['id'],
            'version_number': 1,
            'content_hash': content_hash
        }).execute()
        
        return {
            'message': 'Problem created successfully',
            'problem': problem
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500

@problems_bp.route('/<int:problem_id>', methods=['GET'])
@token_required
def get_problem(current_user, problem_id):
    """Get problem details"""
    try:
        problem = db.get_problem(problem_id)
        
        if not problem:
            return {'error': 'Problem not found'}, 404
        
        # Get test cases (visible only for non-students or teachers)
        test_cases = db.get_test_cases(problem_id, include_hidden=current_user['role'] in ['teacher', 'admin'])
        
        # Get hints
        hints = db.client.table('hints').select('*').eq('problem_id', problem_id).order('level').execute()
        
        return {
            'problem': problem,
            'test_cases': test_cases,
            'hints': hints.data if hints.data else [],
            'visible_test_count': len([t for t in test_cases if not t.get('is_hidden')])
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@problems_bp.route('/<int:problem_id>', methods=['PUT'])
@teacher_required
def update_problem(current_user, problem_id):
    """Update problem (teacher only)"""
    problem = db.get_problem(problem_id)
    
    if not problem:
        return {'error': 'Problem not found'}, 404
    
    # Check authorization
    if problem['created_by'] != current_user['id']:
        return {'error': 'You do not have permission to update this problem'}, 403
    
    data = request.get_json()
    
    try:
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'difficulty' in data:
            if data['difficulty'] not in ['easy', 'medium', 'hard']:
                return {'error': 'Difficulty must be easy, medium, or hard'}, 400
            update_data['difficulty'] = data['difficulty']
        if 'starter_code' in data:
            update_data['starter_code'] = data['starter_code']
        if 'explanation' in data:
            update_data['explanation'] = data['explanation']
        
        if not update_data:
            return {'error': 'No fields to update'}, 400
        
        updated_problem = db.client.table('problems').update(update_data).eq('id', problem_id).execute()
        
        return {
            'message': 'Problem updated successfully',
            'problem': updated_problem.data[0] if updated_problem.data else None
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@problems_bp.route('/<int:problem_id>', methods=['DELETE'])
@teacher_required
def delete_problem(current_user, problem_id):
    """Delete problem (teacher only)"""
    problem = db.get_problem(problem_id)
    
    if not problem:
        return {'error': 'Problem not found'}, 404
    
    # Check authorization
    if problem['created_by'] != current_user['id']:
        return {'error': 'You do not have permission to delete this problem'}, 403
    
    try:
        db.client.table('problems').delete().eq('id', problem_id).execute()
        return {'message': 'Problem deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500

# ============ TEST CASE ENDPOINTS ============

@problems_bp.route('/<int:problem_id>/test-cases', methods=['POST'])
@teacher_required
def add_test_case(current_user, problem_id):
    """Add test case to problem (teacher only)"""
    problem = db.get_problem(problem_id)
    
    if not problem:
        return {'error': 'Problem not found'}, 404
    
    if problem['created_by'] != current_user['id']:
        return {'error': 'You do not have permission to modify this problem'}, 403
    
    data = request.get_json()
    
    if not data or 'input' not in data or 'expected_output' not in data:
        return {'error': 'Missing required fields: input, expected_output'}, 400
    
    try:
        test_case = db.create_test_case(
            problem_id=problem_id,
            input_data=data['input'],
            expected_output=data['expected_output'],
            is_hidden=data.get('is_hidden', False)
        )
        
        return {
            'message': 'Test case added successfully',
            'test_case': test_case
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500

# ============ HINT ENDPOINTS ============

@problems_bp.route('/<int:problem_id>/hints', methods=['POST'])
@teacher_required
def add_hint(current_user, problem_id):
    """Add hint to problem (teacher only)"""
    problem = db.get_problem(problem_id)
    
    if not problem:
        return {'error': 'Problem not found'}, 404
    
    if problem['created_by'] != current_user['id']:
        return {'error': 'You do not have permission to modify this problem'}, 403
    
    data = request.get_json()
    
    if not data or 'level' not in data or 'content' not in data:
        return {'error': 'Missing required fields: level, content'}, 400
    
    try:
        hint = db.client.table('hints').insert({
            'problem_id': problem_id,
            'level': data['level'],
            'content': data['content']
        }).execute()
        
        return {
            'message': 'Hint added successfully',
            'hint': hint.data[0] if hint.data else None
        }, 201
    except Exception as e:
        return {'error': str(e)}, 500
