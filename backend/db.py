"""
Supabase Database Client
"""

import json
import os
from datetime import datetime, timezone
from supabase import create_client, Client
from werkzeug.security import generate_password_hash

from backend.local_db import LocalDB

class SupabaseDB:
    """Supabase database client wrapper"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
        return cls._instance

    def _initialize(self):
        """Initialize Supabase, or a real local SQLite backend for development."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        if not supabase_url or not supabase_key:
            if os.getenv('FLASK_ENV', 'development').lower() == 'production':
                raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set for backend database operations")
            self._local_backend = LocalDB()
            self._client = self._local_backend.client
            return
        self._client = create_client(supabase_url, supabase_key)

    @property
    def client(self) -> Client:
        if self._client is None:
            self._initialize()
        return self._client

    def get_client(self) -> Client:
        """Get Supabase client"""
        return self.client

    # ============ USER OPERATIONS ============
    
    def create_user(self, email: str, password: str, name: str, role: str = 'student'):
        """Create a new user"""
        try:
            response = self.client.table('users').insert({
                'email': email,
                'name': name,
                'password_hash': generate_password_hash(password),
                'role': role,
                'requested_role': None,
                'teacher_approval_status': 'pending' if role == 'teacher' else 'approved'
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    def get_user(self, user_id: int):
        """Get user by ID"""
        response = self.client.table('users').select('*').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        response = self.client.table('users').select('*').eq('email', email).execute()
        return response.data[0] if response.data else None

    def get_user_by_auth_id(self, auth_user_id: str):
        """Get a local user linked to a Supabase Auth identity."""
        response = self.client.table('users').select('*').eq('auth_user_id', auth_user_id).execute()
        return response.data[0] if response.data else None

    def ensure_external_user(
        self,
        *,
        auth_user_id: str,
        email: str,
        name: str,
        provider: str,
        avatar_url: str = None,
    ):
        """Link or create a local role record for an OTP/OAuth identity."""
        user = self.get_user_by_auth_id(auth_user_id) or self.get_user_by_email(email)
        identity_data = {
            'auth_user_id': auth_user_id,
            'auth_provider': provider,
        }
        if avatar_url:
            identity_data['avatar_url'] = avatar_url
        if user:
            return self.update_user(user['id'], identity_data)
        identity_data.update({
            'email': email,
            'name': name or email.split('@')[0],
            'password_hash': None,
            'role': 'student',
            'requested_role': None,
            'teacher_approval_status': 'approved',
        })
        response = self.client.table('users').insert(identity_data).execute()
        return response.data[0] if response.data else None

    def request_email_otp(self, email: str, redirect_to: str = None):
        """Ask Supabase Auth to send its configured email OTP template."""
        options = {'should_create_user': True}
        if redirect_to:
            options['email_redirect_to'] = redirect_to
        return self.client.auth.sign_in_with_otp({'email': email, 'options': options})

    def verify_email_otp(self, email: str, code: str):
        """Verify a Supabase email OTP and return the Auth session."""
        return self.client.auth.verify_otp({'email': email, 'token': code, 'type': 'email'})

    def google_login_url(self, redirect_to: str):
        """Return the Supabase-hosted Google OAuth authorization URL."""
        response = self.client.auth.sign_in_with_oauth({
            'provider': 'google',
            'options': {'redirect_to': redirect_to},
        })
        return response.url

    def exchange_google_code(self, code: str):
        """Exchange the OAuth callback code for a Supabase Auth session."""
        return self.client.auth.exchange_code_for_session({'auth_code': code})

    def request_password_reset(self, email: str, redirect_to: str = None):
        """Request password recovery through Supabase or create a local SQLite token."""
        _ = self.client
        local_backend = getattr(self, '_local_backend', None)
        if local_backend is not None:
            return {'token': local_backend.request_password_reset(email), 'provider': 'local'}
        options = {}
        if redirect_to:
            options['redirect_to'] = redirect_to
        return self.client.auth.reset_password_for_email(email, options)

    def consume_password_reset(self, token: str, password_hash: str):
        """Consume a local one-time reset token. Production recovery is handled by Supabase Auth."""
        _ = self.client
        local_backend = getattr(self, '_local_backend', None)
        if local_backend is None:
            raise RuntimeError('Production password recovery must be completed through Supabase Auth.')
        return local_backend.consume_password_reset(token, password_hash)

    def update_user(self, user_id: int, data: dict):
        """Update user"""
        response = self.client.table('users').update(data).eq('id', user_id).execute()
        return response.data[0] if response.data else None

    def get_pending_teacher_requests(self):
        """Return users who requested teacher approval."""
        response = (
            self.client.table('users')
            .select('id,email,name,role,requested_role,teacher_approval_status,created_at')
            .eq('requested_role', 'teacher')
            .eq('teacher_approval_status', 'pending')
            .execute()
        )
        return response.data or []
    
    # ============ COURSE OPERATIONS ============
    
    def create_course(self, title: str, description: str, created_by: int):
        """Create a new course"""
        response = self.client.table('courses').insert({
            'title': title,
            'description': description,
            'created_by': created_by
        }).execute()
        return response.data[0] if response.data else None
    
    def get_courses(self, limit: int = 100, offset: int = 0):
        """Get all courses"""
        response = self.client.table('courses').select('*').range(offset, offset + limit - 1).execute()
        return response.data
    
    def get_course(self, course_id: int):
        """Get a course with ordered modules and lessons for the learning path UI."""
        response = self.client.table('courses').select('*').eq('id', course_id).execute()
        if not response.data:
            return None
        course = response.data[0]
        modules_response = (
            self.client.table('modules')
            .select('*')
            .eq('course_id', course_id)
            .order('position')
            .execute()
        )
        modules = modules_response.data or []
        for module in modules:
            lessons_response = (
                self.client.table('lessons')
                .select('*')
                .eq('module_id', module['id'])
                .order('position')
                .execute()
            )
            module['lessons'] = lessons_response.data or []
        course['modules'] = modules
        return course
    
    def get_course_for_user(self, course_id: int, user_id: int):
        """Return a course decorated with user-owned realtime lesson status."""
        course = self.get_course(course_id)
        if not course:
            return None
        progress_response = self.client.table('lesson_progress').select('lesson_id,status,started_at,completed_at').eq('user_id', user_id).execute()
        completed = {row['lesson_id']: row for row in (progress_response.data or [])}
        total_lessons = 0
        completed_lessons = 0
        for module in course.get('modules', []):
            lessons = module.get('lessons', [])
            module_completed = 0
            for lesson in lessons:
                total_lessons += 1
                record = completed.get(lesson['id'])
                status = (record or {}).get('status') or ('completed' if (record or {}).get('completed_at') else 'not_started')
                lesson['status'] = status
                lesson['complete'] = status == 'completed'
                lesson['started_at'] = (record or {}).get('started_at')
                lesson['completed_at'] = (record or {}).get('completed_at')
                if status == 'completed':
                    completed_lessons += 1
                    module_completed += 1
            module['completed_lessons'] = module_completed
            module['lesson_count'] = len(lessons)
            module['status'] = 'completed' if lessons and module_completed == len(lessons) else ('in_progress' if module_completed else 'not_started')
            module['complete'] = bool(lessons) and module_completed == len(lessons)
        course['completed_lessons'] = completed_lessons
        course['lesson_count'] = total_lessons
        course['progress'] = round((completed_lessons / total_lessons) * 100) if total_lessons else 0
        return course

    def get_courses_for_user(self, user_id: int, limit: int = 100, offset: int = 0):
        """Return all published courses with per-user progress."""
        courses = self.get_courses(limit=limit, offset=offset)
        return [self.get_course_for_user(course['id'], user_id) for course in courses]

    def start_lesson(self, user_id: int, lesson_id: int):
        """Persist a learner's in-progress lesson state."""
        response = self.client.table('lesson_progress').upsert({
            'user_id': user_id,
            'lesson_id': lesson_id,
            'status': 'in_progress',
        }).execute()
        return response.data[0] if response.data else None

    def complete_lesson(self, user_id: int, lesson_id: int):
        """Persist a learner's completed lesson state."""
        response = self.client.table('lesson_progress').upsert({
            'user_id': user_id,
            'lesson_id': lesson_id,
            'status': 'completed',
            'completed_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
        return response.data[0] if response.data else None

    # ============ ASSESSMENT OPERATIONS ============

    @staticmethod
    def _question_payload(question, include_answers=False):
        item = dict(question or {})
        options = item.get('options', [])
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except (TypeError, ValueError):
                options = []
        item['options'] = options or []
        if not include_answers:
            item.pop('correct_answer', None)
            item.pop('explanation', None)
        return item

    def create_exam(self, data: dict, created_by: int):
        exam_payload = {
            'title': data['title'].strip(),
            'description': str(data.get('description', '')).strip(),
            'duration_minutes': int(data.get('duration_minutes', 20)),
            'max_attempts': int(data.get('max_attempts', 3)),
            'status': data.get('status', 'published'),
            'created_by': created_by,
        }
        exam_response = self.client.table('exams').insert(exam_payload).execute()
        exam = exam_response.data[0] if exam_response.data else None
        if not exam:
            return None
        questions = []
        for position, question in enumerate(data.get('questions', []), start=1):
            payload = {
                'exam_id': exam['id'],
                'position': int(question.get('position', position)),
                'question_type': question.get('question_type', 'multiple_choice'),
                'prompt': str(question.get('prompt', '')).strip(),
                'options': question.get('options', []),
                'correct_answer': question.get('correct_answer'),
                'points': float(question.get('points', 1)),
                'explanation': str(question.get('explanation', '')).strip(),
            }
            response = self.client.table('exam_questions').insert(payload).execute()
            if response.data:
                questions.append(response.data[0])
        exam['questions'] = questions
        return exam

    def get_exam(self, exam_id: int, include_answers=False):
        response = self.client.table('exams').select('*').eq('id', exam_id).execute()
        if not response.data:
            return None
        exam = dict(response.data[0])
        question_response = self.client.table('exam_questions').select('*').eq('exam_id', exam_id).order('position').execute()
        exam['questions'] = [self._question_payload(question, include_answers=include_answers) for question in (question_response.data or [])]
        return exam

    def get_exams_for_user(self, user_id: int, role: str = 'student'):
        query = self.client.table('exams').select('*').order('created_at', desc=True)
        if role == 'student':
            query = query.eq('status', 'published')
        response = query.execute()
        exams = []
        for row in response.data or []:
            exam = dict(row)
            questions = self.client.table('exam_questions').select('id,position,question_type,points').eq('exam_id', exam['id']).order('position').execute().data or []
            attempts = self.client.table('exam_attempts').select('id,status,score,started_at,submitted_at').eq('exam_id', exam['id']).eq('user_id', user_id).order('started_at', desc=True).execute().data or []
            exam['question_count'] = len(questions)
            exam['attempt_count'] = len(attempts)
            exam['best_score'] = max([float(item.get('score', 0) or 0) for item in attempts], default=None)
            exam['latest_attempt'] = attempts[0] if attempts else None
            exams.append(exam)
        return exams

    def start_exam(self, exam_id: int, user_id: int):
        exam = self.get_exam(exam_id, include_answers=False)
        if not exam or exam.get('status') != 'published':
            return None, 'exam_not_available'
        active = self.client.table('exam_attempts').select('*').eq('exam_id', exam_id).eq('user_id', user_id).eq('status', 'in_progress').order('started_at', desc=True).execute().data or []
        if active:
            return self.get_attempt(active[0]['id'], user_id=user_id, include_answers=False), None
        attempts = self.client.table('exam_attempts').select('id').eq('exam_id', exam_id).eq('user_id', user_id).execute().data or []
        if len(attempts) >= int(exam.get('max_attempts', 3) or 3):
            return None, 'attempt_limit_reached'
        total_points = sum(float(question.get('points', 1) or 1) for question in exam.get('questions', []))
        response = self.client.table('exam_attempts').insert({
            'exam_id': exam_id,
            'user_id': user_id,
            'status': 'in_progress',
            'total_points': total_points,
        }).execute()
        attempt = response.data[0] if response.data else None
        return (self.get_attempt(attempt['id'], user_id=user_id, include_answers=False) if attempt else None), None

    def get_attempt(self, attempt_id: int, user_id: int | None = None, include_answers=False):
        query = self.client.table('exam_attempts').select('*').eq('id', attempt_id)
        if user_id is not None:
            query = query.eq('user_id', user_id)
        response = query.execute()
        if not response.data:
            return None
        attempt = dict(response.data[0])
        attempt['exam'] = self.get_exam(attempt['exam_id'], include_answers=include_answers)
        answers = self.client.table('exam_answers').select('*').eq('attempt_id', attempt_id).execute().data or []
        attempt['answers'] = answers
        return attempt

    def save_exam_answer(self, attempt_id: int, question_id: int, answer: str):
        response = self.client.table('exam_answers').upsert({
            'attempt_id': attempt_id,
            'question_id': question_id,
            'answer': str(answer or ''),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
        return response.data[0] if response.data else None

    def submit_exam(self, attempt_id: int, user_id: int):
        attempt = self.get_attempt(attempt_id, user_id=user_id, include_answers=True)
        if not attempt:
            return None, 'attempt_not_found'
        if attempt.get('status') in {'submitted', 'graded', 'expired'}:
            return attempt, None
        started_at = attempt.get('started_at')
        if started_at:
            try:
                parsed = datetime.fromisoformat(str(started_at).replace('Z', '+00:00'))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                elapsed = (datetime.now(timezone.utc) - parsed).total_seconds() / 60
                if elapsed > float(attempt['exam'].get('duration_minutes', 20)):
                    status = 'expired'
                else:
                    status = 'graded'
            except (TypeError, ValueError):
                status = 'graded'
        else:
            status = 'graded'
        answers_by_question = {item['question_id']: item for item in attempt.get('answers', [])}
        earned = 0.0
        total = 0.0
        for question in attempt['exam'].get('questions', []):
            points = float(question.get('points', 1) or 1)
            total += points
            answer = answers_by_question.get(question['id'], {}).get('answer', '')
            expected = str(question.get('correct_answer', '') or '').strip().casefold()
            actual = str(answer or '').strip().casefold()
            correct = bool(expected and actual == expected)
            item_score = points if correct else 0.0
            earned += item_score
            self.client.table('exam_answers').upsert({
                'attempt_id': attempt_id,
                'question_id': question['id'],
                'answer': answer,
                'is_correct': correct,
                'earned_points': item_score,
                'feedback': question.get('explanation', '') if correct or status != 'in_progress' else '',
                'updated_at': datetime.now(timezone.utc).isoformat(),
            }).execute()
        score = round((earned / total) * 100, 2) if total else 0
        updated = self.client.table('exam_attempts').update({
            'status': status,
            'score': score,
            'earned_points': earned,
            'total_points': total,
            'submitted_at': datetime.now(timezone.utc).isoformat(),
            'graded_at': datetime.now(timezone.utc).isoformat(),
        }).eq('id', attempt_id).eq('user_id', user_id).execute()
        final_attempt = self.get_attempt(attempt_id, user_id=user_id, include_answers=False)
        if final_attempt:
            final_attempt['result_answers'] = self.client.table('exam_answers').select('*').eq('attempt_id', attempt_id).execute().data or []
            # The submit endpoint is student-only. Return result feedback but
            # never send the answer key or teacher explanation source fields.
            final_attempt['exam'] = self.get_exam(attempt['exam_id'], include_answers=False)
        return final_attempt or attempt, None

    def get_exam_report(self, exam_id: int):
        exam = self.get_exam(exam_id, include_answers=True)
        if not exam:
            return None
        attempts = self.client.table('exam_attempts').select('*').eq('exam_id', exam_id).order('submitted_at', desc=True).execute().data or []
        submitted = [item for item in attempts if item.get('status') in {'submitted', 'graded'}]
        scores = [float(item.get('score', 0) or 0) for item in submitted]
        return {
            'exam': {key: value for key, value in exam.items() if key != 'questions'},
            'question_count': len(exam.get('questions', [])),
            'attempt_count': len(attempts),
            'submitted_count': len(submitted),
            'average_score': round(sum(scores) / len(scores), 2) if scores else 0,
            'highest_score': max(scores, default=0),
            'pass_rate': round(sum(1 for score in scores if score >= 60) / len(scores) * 100, 2) if scores else 0,
            'distribution': {'excellent': sum(1 for score in scores if score >= 80), 'pass': sum(1 for score in scores if 60 <= score < 80), 'needs_review': sum(1 for score in scores if score < 60)},
        }

    def get_progress_report(self, user_id: int):
        progress = self.get_user_lesson_progress(user_id) or []
        courses = self.get_courses_for_user(user_id)
        attempts = self.client.table('exam_attempts').select('id,exam_id,status,score,started_at,submitted_at').eq('user_id', user_id).order('started_at', desc=True).execute().data or []
        mastery = self.get_user_mastery(user_id) or []
        completed = len([item for item in progress if item.get('status') == 'completed' or item.get('completed_at')])
        return {
            'summary': {'lessons_started': len(progress), 'lessons_completed': completed, 'courses_active': len([course for course in courses if float(course.get('progress', 0) or 0) < 100]), 'average_mastery': round(sum(float(item.get('mastery_score', 0) or 0) for item in mastery) / len(mastery), 2) if mastery else 0},
            'courses': [{'id': course.get('id'), 'title': course.get('title'), 'progress': course.get('progress', 0), 'completed_lessons': course.get('completed_lessons', 0), 'lesson_count': course.get('lesson_count', 0)} for course in courses],
            'exams': attempts,
            'mastery': mastery,
        }

    # ============ CLASS OPERATIONS ============
    
    def create_class(self, course_id: int, teacher_id: int, name: str, enrollment_code: str):
        """Create a new class"""
        response = self.client.table('classes').insert({
            'course_id': course_id,
            'teacher_id': teacher_id,
            'name': name,
            'enrollment_code': enrollment_code
        }).execute()
        return response.data[0] if response.data else None
    
    def get_class(self, class_id: int):
        """Get class by ID"""
        response = self.client.table('classes').select('*').eq('id', class_id).execute()
        return response.data[0] if response.data else None
    
    def get_teacher_classes(self, teacher_id: int):
        """Get all classes for a teacher"""
        response = self.client.table('classes').select('*').eq('teacher_id', teacher_id).execute()
        return response.data or []

    def get_all_classes(self):
        """Get all classes for owner/admin dashboards."""
        response = self.client.table('classes').select('*').execute()
        return response.data or []
    
    # ============ PROBLEM OPERATIONS ============
    
    def create_problem(self, title: str, description: str, difficulty: str, 
                      starter_code: str, created_by: int, language: str = 'python'):
        """Create a new problem"""
        response = self.client.table('problems').insert({
            'title': title,
            'description': description,
            'difficulty': difficulty,
            'starter_code': starter_code,
            'created_by': created_by,
            'language': language
        }).execute()
        return response.data[0] if response.data else None
    
    def get_problem(self, problem_id: int):
        """Get problem by ID"""
        response = self.client.table('problems').select('*').eq('id', problem_id).execute()
        return response.data[0] if response.data else None
    
    def get_problems(self, limit: int = 100, offset: int = 0):
        """Get all problems"""
        response = self.client.table('problems').select('*').range(offset, offset + limit - 1).execute()
        return response.data
    
    # ============ SUBMISSION OPERATIONS ============
    
    def create_submission(self, user_id: int, problem_id: int, code: str, 
                         assignment_id: int = None, exam_id: int = None):
        """Create a new submission"""
        response = self.client.table('submissions').insert({
            'user_id': user_id,
            'problem_id': problem_id,
            'code': code,
            'assignment_id': assignment_id,
            'exam_id': exam_id,
            'status': 'pending'
        }).execute()
        return response.data[0] if response.data else None
    
    def get_submission(self, submission_id: int):
        """Get submission by ID"""
        response = self.client.table('submissions').select('*').eq('id', submission_id).execute()
        return response.data[0] if response.data else None

    def get_user_submissions(self, user_id: int, limit: int = 5):
        """Get a user's most recent submissions with problem display metadata."""
        response = (
            self.client.table('submissions')
            .select('*, problems(title, difficulty)')
            .eq('user_id', user_id)
            .order('created_at', desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    
    def get_user_lesson_progress(self, user_id: int):
        """Get lessons completed by a user."""
        response = self.client.table('lesson_progress').select('*').eq('user_id', user_id).order('completed_at', desc=True).execute()
        return response.data or []

    def update_submission_status(self, submission_id: int, status: str, score: float = None):
        """Update submission status"""
        data = {'status': status}
        if score is not None:
            data['score'] = score
        response = self.client.table('submissions').update(data).eq('id', submission_id).execute()
        return response.data[0] if response.data else None
    
    # ============ TEST CASE OPERATIONS ============
    
    def create_test_case(self, problem_id: int, input_data: str, expected_output: str, is_hidden: bool = False):
        """Create a test case"""
        response = self.client.table('test_cases').insert({
            'problem_id': problem_id,
            'input': input_data,
            'expected_output': expected_output,
            'is_hidden': is_hidden
        }).execute()
        return response.data[0] if response.data else None
    
    def get_test_cases(self, problem_id: int, include_hidden: bool = False):
        """Get test cases for a problem"""
        response = self.client.table('test_cases').select('*').eq('problem_id', problem_id)
        if not include_hidden:
            response = response.eq('is_hidden', False)
        return response.execute().data
    
    # ============ SKILL OPERATIONS ============
    
    def create_skill(self, name: str, description: str, category: str = None):
        """Create a new skill"""
        response = self.client.table('skills').insert({
            'name': name,
            'description': description,
            'category': category
        }).execute()
        return response.data[0] if response.data else None
    
    def get_skills(self):
        """Get all skills"""
        response = self.client.table('skills').select('*').execute()
        return response.data
    
    # ============ MASTERY OPERATIONS ============
    
    def get_user_mastery(self, user_id: int, skill_id: int = None):
        """Get user mastery for a skill or all skills"""
        query = self.client.table('mastery_snapshots').select('*').eq('user_id', user_id)
        if skill_id:
            query = query.eq('skill_id', skill_id)
        response = query.execute()
        return response.data
    
    def update_mastery(self, user_id: int, skill_id: int, mastery_score: float,
                      first_attempt_success_rate: float = None, retry_recovery_rate: float = None,
                      hint_usage_count: int = None):
        """Update user mastery"""
        data = {
            'user_id': user_id,
            'skill_id': skill_id,
            'mastery_score': mastery_score
        }
        if first_attempt_success_rate is not None:
            data['first_attempt_success_rate'] = first_attempt_success_rate
        if retry_recovery_rate is not None:
            data['retry_recovery_rate'] = retry_recovery_rate
        if hint_usage_count is not None:
            data['hint_usage_count'] = hint_usage_count
        
        # Try to update, if not found insert
        response = self.client.table('mastery_snapshots').upsert(data).execute()
        return response.data[0] if response.data else None

# Singleton instance
db = SupabaseDB()
