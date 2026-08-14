"""
Analytics Routes
Learning analytics and progress tracking
"""

from flask import Blueprint, request, jsonify
from backend.api.auth import token_required
from backend.db import db
from backend.rbac import permission_required

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
@permission_required('student.dashboard.read')
def get_student_dashboard(current_user):
    """Return normalized dashboard data for the authenticated student."""
    try:
        mastery_data = db.get_user_mastery(current_user['id']) or []
        submissions = db.get_user_submissions(current_user['id'], limit=5) or []
        recent_practice = []
        for submission in submissions:
            problem = submission.get('problems') or {}
            score = submission.get('score')
            recent_practice.append({
                'id': submission.get('id'),
                'title': problem.get('title') or f"Problem #{submission.get('problem_id')}",
                'category': problem.get('difficulty', 'Practice').title(),
                'status': submission.get('status', 'pending').replace('_', ' ').title(),
                'score': f"{float(score):.0f}%" if score is not None else '—',
                'icon': str(submission.get('problem_id', 0)).zfill(2),
                'created_at': submission.get('created_at')
            })
        return {
            'user_id': current_user['id'],
            'mastery': mastery_data,
            'skills': mastery_data,
            'recentPractice': recent_practice,
            'recent_practice': recent_practice,
            'total_skills': len(mastery_data),
            'message': 'Student dashboard loaded.',
            'message_mn': 'Суралцагчийн хяналтын самбар ачааллаа.'
        }, 200
    except Exception:
        return {
            'error': {
                'code': 'student_dashboard_failed',
                'message': 'The student dashboard could not be loaded.',
                'message_mn': 'Суралцагчийн хяналтын самбар ачаалахад алдаа гарлаа.'
            }
        }, 500

@analytics_bp.route('/mastery/<int:user_id>', methods=['GET'])
@token_required
def get_user_mastery(current_user, user_id):
    """Get user mastery for all skills"""
    # Check authorization
    if current_user['id'] != user_id and current_user['role'] not in ['owner', 'admin', 'teacher']:
        return {
            'error': {
                'code': 'permission_denied',
                'message': 'You do not have permission to view this data.',
                'message_mn': 'Танд энэ мэдээллийг харах зөвшөөрөл байхгүй байна.'
            }
        }, 403
    
    try:
        mastery_data = db.get_user_mastery(user_id)
        
        return {
            'user_id': user_id,
            'mastery': mastery_data if mastery_data else [],
            'total_skills': len(mastery_data) if mastery_data else 0
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@analytics_bp.route('/skill/<int:skill_id>', methods=['GET'])
@token_required
def get_skill_statistics(current_user, skill_id):
    """Get statistics for a skill"""
    try:
        # Get all users' mastery for this skill
        mastery_data = db.client.table('mastery_snapshots').select('*').eq('skill_id', skill_id).execute()
        
        if not mastery_data.data:
            return {
                'skill_id': skill_id,
                'statistics': {
                    'total_students': 0,
                    'average_mastery': 0,
                    'distribution': {}
                }
            }, 200
        
        scores = [m.get('mastery_score', 0) for m in mastery_data.data]
        average = sum(scores) / len(scores) if scores else 0
        
        return {
            'skill_id': skill_id,
            'statistics': {
                'total_students': len(mastery_data.data),
                'average_mastery': average,
                'min_mastery': min(scores) if scores else 0,
                'max_mastery': max(scores) if scores else 0
            }
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500

@analytics_bp.route('/problem/<int:problem_id>', methods=['GET'])
@token_required
def get_problem_statistics(current_user, problem_id):
    """Get statistics for a problem"""
    try:
        problem = db.get_problem(problem_id)
        
        if not problem:
            return {'error': 'Problem not found'}, 404
        
        # Get submissions
        submissions = db.client.table('submissions').select('*').eq('problem_id', problem_id).execute()
        
        if not submissions.data:
            return {
                'problem_id': problem_id,
                'statistics': {
                    'total_submissions': 0,
                    'acceptance_rate': 0,
                    'average_score': 0
                }
            }, 200
        
        total = len(submissions.data)
        accepted = len([s for s in submissions.data if s.get('status') == 'accepted'])
        scores = [s.get('score', 0) for s in submissions.data]
        average_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'problem_id': problem_id,
            'statistics': {
                'total_submissions': total,
                'accepted_submissions': accepted,
                'acceptance_rate': (accepted / total * 100) if total > 0 else 0,
                'average_score': average_score,
                'difficulty': problem.get('difficulty')
            }
        }, 200
    except Exception as e:
        return {'error': str(e)}, 500
