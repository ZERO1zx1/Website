"""
Submissions Routes
Code submission and evaluation management
"""

from flask import Blueprint, Response, request, jsonify, stream_with_context
import json
import time

from backend.api.auth import token_required, teacher_required
from backend.db import db
from backend.services.submission_queue import enqueue_submission
from backend.services.code_executor import get_executor
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
        language = str(data.get('language') or problem.get('language') or 'python').lower()
        if language not in {'python', 'javascript'}:
            return {'error': 'Unsupported language'}, 400

        submission = db.create_submission(
            user_id=current_user['id'],
            problem_id=data['problem_id'],
            code=data['code'],
            assignment_id=data.get('assignment_id'),
            exam_id=data.get('exam_id')
        )
        if not submission:
            return {'error': 'Submission could not be created'}, 500

        try:
            enqueue_submission(
                submission_id=submission['id'],
                user_id=current_user['id'],
                problem_id=data['problem_id'],
                code=data['code'],
                language=language,
            )
        except Exception:
            db.update_submission_status(submission['id'], 'error')
            return {'error': 'Submission evaluator is temporarily unavailable'}, 503

        return {
            'message': 'Submission received. Evaluating...',
            'submission': {
                'id': submission['id'],
                'status': submission['status'],
                'language': language,
                'created_at': submission['created_at']
            }
        }, 202
    except Exception:
        return {'error': 'Submission service unavailable'}, 503

@submissions_bp.route('/run', methods=['POST'])
@token_required
def run_code(current_user):
    """Execute code against visible test cases without creating a graded submission."""
    if current_user['role'] != 'student':
        return {'error': 'Only students can run code'}, 403
    data = request.get_json(silent=True) or {}
    if not data.get('problem_id') or not isinstance(data.get('code'), str) or not data['code'].strip():
        return {'error': 'Missing required fields: problem_id, code'}, 400
    try:
        problem = db.get_problem(data['problem_id'])
        if not problem:
            return {'error': 'Problem not found'}, 404
        language = str(data.get('language') or problem.get('language') or 'python').lower()
        if language not in {'python', 'javascript'}:
            return {'error': 'Unsupported language'}, 400
        test_cases = db.get_test_cases(data['problem_id'], include_hidden=False)
        if not test_cases:
            return {'error': 'No visible test cases are available'}, 409
        result = get_executor().execute_test_cases(
            code=data['code'],
            language=language,
            test_cases=test_cases,
        )
        return {'mode': 'runtime', 'problem_id': data['problem_id'], **result}, 200
    except Exception:
        return {'error': 'Runtime execution is temporarily unavailable'}, 503


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
    except Exception:
        return {'error': 'Submission result unavailable'}, 503

@submissions_bp.route('/<int:submission_id>/stream', methods=['GET'])
@token_required
def stream_submission(current_user, submission_id):
    """Stream submission state changes until a final evaluator status is reached."""
    submission = db.get_submission(submission_id)
    if not submission:
        return {'error': 'Submission not found'}, 404
    if submission['user_id'] != current_user['id'] and current_user['role'] not in ['teacher', 'admin']:
        return {'error': 'You do not have permission to view this submission'}, 403

    @stream_with_context
    def events():
        last_signature = None
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            current = db.get_submission(submission_id)
            results = db.client.table('submission_results').select('*').eq('submission_id', submission_id).execute()
            payload = {
                'submission': current,
                'results': results.data if results.data else [],
            }
            signature = json.dumps(payload, sort_keys=True, default=str)
            if signature != last_signature:
                yield f"event: submission\\ndata: {json.dumps(payload, default=str)}\\n\\n"
                last_signature = signature
            if current and current.get('status') in {'accepted', 'partial_accepted', 'rejected', 'error'}:
                break
            time.sleep(1)

    return Response(
        events(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no', 'Connection': 'keep-alive'},
    )


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
    except Exception:
        return {'error': 'Submission history unavailable'}, 503
