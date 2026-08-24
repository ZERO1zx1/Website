"""
Submissions Routes
Code submission and evaluation management
"""

import json
import os
import time

from flask import Blueprint, Response, request, stream_with_context

from backend.api.auth import token_required
from backend.db import db
from backend.services.code_executor import get_executor
from backend.services.gamification import award_xp, record_activity
from backend.services.submission_queue import enqueue_submission
from learning_experiences import get_challenge

submissions_bp = Blueprint('submissions', __name__)


def _execution_enabled():
    return bool(os.getenv('SANDBOX_URL')) or os.getenv(
        'ALLOW_LOCAL_DOCKER_SANDBOX', 'false'
    ).lower() == 'true'


def _visible_results(results, current_user):
    if current_user.get('role') in {'teacher', 'admin', 'owner'}:
        return results
    visible = []
    for result in results:
        item = dict(result)
        if item.get('is_hidden'):
            for key in ('expected_output', 'input', 'error'):
                item.pop(key, None)
        visible.append(item)
    return visible

# ============ SUBMISSION ENDPOINTS ============

@submissions_bp.route('', methods=['POST'])
@token_required
def create_submission(current_user):
    """Submit code for evaluation"""
    if current_user['role'] != 'student':
        return {'error': 'Only students can submit code'}, 403
    if not _execution_enabled():
        return {'error': 'Code execution is disabled until the sandbox is configured'}, 503
    
    data = request.get_json()
    
    if not data or 'problem_id' not in data or 'code' not in data:
        return {'error': 'Missing required fields: problem_id, code'}, 400
    
    try:
        problem = db.get_problem(data['problem_id'])
        
        if not problem:
            return {'error': 'Problem not found'}, 404
        
        # Create submission
        language = str(data.get('language') or problem.get('language') or 'python').lower()
        if language not in {'python', 'javascript', 'html', 'css'}:
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
    """Execute a DB problem or a published/static catalog challenge without saving a submission."""
    if current_user['role'] != 'student':
        return {'error': 'Only students can run code'}, 403
    if not _execution_enabled():
        return {'error': 'Code execution is disabled until the sandbox is configured'}, 503
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get('code'), str) or not data['code'].strip():
        return {'error': 'Missing required field: code'}, 400
    challenge_id = data.get('challenge_id')
    try:
        if challenge_id:
            challenge = get_challenge(str(challenge_id))
            if not challenge:
                return {'error': 'Challenge not found'}, 404
            language = str(data.get('language') or challenge.get('course_id') or 'python').lower()
            test_cases = [item for item in challenge.get('tests', []) if not item.get('is_hidden')]
            if not test_cases and challenge.get('expected_output'):
                test_cases = [{'input': '', 'expected_output': challenge['expected_output'], 'is_hidden': False}]
            if not test_cases:
                return {'error': 'No visible test cases are available'}, 409
            result = get_executor().execute_test_cases(
                code=data['code'], language=language, test_cases=test_cases,
            )
            return {'mode': 'catalog', 'challenge_id': challenge_id, **result}, 200

        if not data.get('problem_id'):
            return {'error': 'Missing problem_id or challenge_id'}, 400
        problem = db.get_problem(data['problem_id'])
        if not problem:
            return {'error': 'Problem not found'}, 404
        language = str(data.get('language') or problem.get('language') or 'python').lower()
        if language not in {'python', 'javascript', 'html', 'css'}:
            return {'error': 'Unsupported language'}, 400
        test_cases = db.get_test_cases(data['problem_id'], include_hidden=False)
        if not test_cases:
            return {'error': 'No visible test cases are available'}, 409
        result = get_executor().execute_test_cases(
            code=data['code'], language=language, test_cases=test_cases,
        )
        return {'mode': 'runtime', 'problem_id': data['problem_id'], **result}, 200
    except Exception:
        return {'error': 'Runtime execution is temporarily unavailable'}, 503


@submissions_bp.route('/catalog', methods=['POST'])
@token_required
def submit_catalog_challenge(current_user):
    """Evaluate and persist a static/published catalog challenge attempt."""
    if current_user['role'] != 'student':
        return {'error': 'Only students can submit code'}, 403
    if not _execution_enabled():
        return {'error': 'Code execution is disabled until the sandbox is configured'}, 503
    data = request.get_json(silent=True) or {}
    challenge_id = str(data.get('challenge_id') or '')
    code = data.get('code')
    if not challenge_id or not isinstance(code, str) or not code.strip():
        return {'error': 'Missing required fields: challenge_id, code'}, 400
    challenge = get_challenge(challenge_id)
    if not challenge:
        return {'error': 'Challenge not found'}, 404
    app_user_id = current_user.get('auth_user_id')
    if not app_user_id:
        return {'error': 'Local app identity is required'}, 409
    language = str(data.get('language') or challenge.get('course_id') or 'python').lower()
    if language not in {'python', 'javascript', 'html', 'css'}:
        return {'error': 'Unsupported language'}, 400
    test_cases = challenge.get('tests') or []
    if not test_cases and challenge.get('expected_output'):
        test_cases = [{'input': '', 'expected_output': challenge['expected_output'], 'is_hidden': False}]
    if not test_cases:
        return {'error': 'No test cases are available'}, 409
    try:
        results = get_executor().execute_test_cases(code=code, language=language, test_cases=test_cases)
        visible_results = _visible_results(results.get('test_results', []), current_user)
        results = {**results, 'test_results': visible_results}
        attempt = db.create_catalog_attempt(app_user_id, challenge_id, language, code, results)
        reward = None
        if results.get('status') == 'accepted':
            xp = int(challenge.get('xp') or 80)
            xp_result = award_xp(int(current_user['id']), f'catalog:{challenge_id}', 'accepted_catalog_challenge', xp, None, {'challenge_id': challenge_id})
            streak = record_activity(int(current_user['id']), 'accepted_catalog_challenge')
            reward = {'xp': xp_result, 'streak': streak}
        return {'mode': 'catalog', 'challenge_id': challenge_id, 'attempt': attempt, 'results': results, 'reward': reward}, 201
    except Exception:
        return {'error': 'Catalog challenge submission is temporarily unavailable'}, 503


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
            'results': _visible_results(results.data or [], current_user)
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
                'results': _visible_results(results.data or [], current_user),
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
