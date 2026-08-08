"""
Submissions Routes
Code submission and evaluation management
"""

from flask import Blueprint, request, jsonify
from routes.auth import token_required, teacher_required
from db import db
from datetime import datetime

submissions_bp = Blueprint('submissions', __name__)

# ============ SUBMISSION ENDPOINTS ============

@submissions_bp.route('', methods=['POST'])
@token_required
def create_submission(current_user):
    """Submit code for evaluation"""
    if current_user['role'] != 'student':
        return {'error': 'Only students can submit code'}, 403
    
    data = request.get_json()
    
    if not data or 'problem_id' not in data or 'code' not in data:
        return {'error': 'Missing required fields: problem_id, code'}, 400
    
    try:
        problem = db.get_problem(data['problem_id'])
        
        if not problem:
            return {'error': 'Problem not found'}, 404
        
        # Create submission
        submission = db.create_submission(
            user_id=current_user['id'],
            problem_id=data['problem_id'],
            code=data['code'],
            assignment_id=data.get('assignment_id'),
            exam_id=data.get('exam_id')
        )
        
        return {
            'message': 'Submission received. Evaluating...',
            'submission': {
                'id': submission['id'],
                'status': submission['status'],
                'created_at': submission['created_at']
            }
        }, 202
    except Exception as e:
        return {'error': str(e)}, 500

@submissions_bp.route('/<int:submission_id>', methods=['GET'])
@token_required
def get_submission(current_user, submission_id):
    """Get submission details and results"""
    try:
        submission = db.get_submission(submission_id)
        
        if not submission:
            return {'error': 'Submission not found'}, 404
        
        # Check authorization
        if submission['user_id'] != current_user['id'] and current_user['role'] not in ['teacher', 'admin']:
            return {'error': 'You do not have permission to view this submission'}, 403
        
        # Get results
        results = db.client.table('submission_results').select('*').eq('submission_id', submission_id).execute()
        
        return {
            'submission': submission,
            'results': results.data if results.data else []
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@submissions_bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_submissions(current_user, user_id):
    """Get user's submissions"""
    # Check authorization
    if current_user['id'] != user_id and current_user['role'] not in ['teacher', 'admin']:
        return {'error': 'You do not have permission to view these submissions'}, 403
    
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        submissions = db.client.table('submissions').select('*').eq('user_id', user_id).range(offset, offset + limit - 1).order('created_at', desc=True).execute()
        
        return {
            'submissions': submissions.data if submissions.data else [],
            'total': len(submissions.data) if submissions.data else 0,
            'limit': limit,
            'offset': offset
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500
