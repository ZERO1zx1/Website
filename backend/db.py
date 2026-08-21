"""
Supabase Database Client
"""

import os

from supabase import Client, create_client


class SupabaseDB:
    """Supabase database client wrapper"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._auth_client = None
        return cls._instance

    def _initialize(self):
        """Initialize Supabase client only when a database operation is requested."""
        supabase_url = os.getenv('SUPABASE_URL')
        # Database mutations made by Flask are server-side operations. The
        # publishable key is intentionally never used as a privileged client.
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set for backend database operations"
            )

        self._client = create_client(supabase_url, supabase_key)

    @property
    def client(self) -> Client:
        if self._client is None:
            self._initialize()
        return self._client

    def _initialize_auth(self):
        """Create a least-privilege client for Supabase Auth browser-equivalent flows."""
        supabase_url = os.getenv('SUPABASE_URL')
        publishable_key = os.getenv('SUPABASE_KEY')
        if not supabase_url or not publishable_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set for Supabase Auth")
        self._auth_client = create_client(supabase_url, publishable_key)

    @property
    def auth_client(self) -> Client:
        if self._auth_client is None:
            self._initialize_auth()
        return self._auth_client

    def user_client(self, access_token: str) -> Client:
        """Create a request-scoped client whose database queries obey the learner's RLS policies."""
        supabase_url = os.getenv('SUPABASE_URL')
        publishable_key = os.getenv('SUPABASE_KEY')
        if not supabase_url or not publishable_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set for user-scoped queries")
        client = create_client(supabase_url, publishable_key)
        client.postgrest.auth(access_token)
        return client

    def get_client(self) -> Client:
        """Get the trusted server-side database client."""
        return self.client

    # ============ SUPABASE AUTH, PROFILE, AND LEARNING PROGRESS ============

    @staticmethod
    def _value(record, key, default=None):
        if isinstance(record, dict):
            return record.get(key, default)
        return getattr(record, key, default)

    def sign_up_with_password(self, email: str, password: str, display_name: str, redirect_to: str = None):
        """Register an Auth user and store display-name metadata for the profile trigger."""
        options = {'data': {'display_name': display_name}}
        if redirect_to:
            options['email_redirect_to'] = redirect_to
        return self.auth_client.auth.sign_up({
            'email': email,
            'password': password,
            'options': options,
        })

    def sign_in_with_password(self, email: str, password: str):
        """Authenticate against Supabase Auth; passwords are never stored in public tables."""
        return self.auth_client.auth.sign_in_with_password({'email': email, 'password': password})

    def get_auth_user(self, access_token: str):
        """Validate a Supabase access token and return its Auth user."""
        response = self.auth_client.auth.get_user(access_token)
        user = self._value(response, 'user')
        if not user:
            raise RuntimeError('Supabase token did not resolve to a user')
        return user

    def ensure_profile(self, auth_user, access_token: str):
        """Return the CodeCraft profile, creating a safe default if a legacy Auth user has none."""
        user_id = str(self._value(auth_user, 'id'))
        email = self._value(auth_user, 'email')
        metadata = self._value(auth_user, 'user_metadata', {}) or {}
        display_name = metadata.get('display_name') or metadata.get('full_name') or metadata.get('name')
        if not display_name and email:
            display_name = email.split('@', 1)[0]
        client = self.user_client(access_token)
        existing = client.table('profiles').select('*').eq('id', user_id).limit(1).execute().data
        if not existing:
            client.table('profiles').upsert({
                'id': user_id,
                'email': email,
                'display_name': display_name,
            }, on_conflict='id').execute()
            existing = client.table('profiles').select('*').eq('id', user_id).limit(1).execute().data
        profile = existing[0] if existing else {'id': user_id, 'email': email, 'display_name': display_name, 'role': 'student'}
        return {
            'id': profile.get('id', user_id),
            'email': profile.get('email') or email,
            'name': profile.get('display_name') or display_name or 'суралцагч',
            'role': profile.get('role', 'student'),
            'locale': profile.get('locale', 'mn'),
            'theme': profile.get('theme', 'system'),
        }

    def get_profile(self, user_id: str, access_token: str):
        """Read the authenticated learner's own CodeCraft profile through RLS."""
        result = self.user_client(access_token).table('profiles').select('*').eq('id', str(user_id)).limit(1).execute().data
        return result[0] if result else None

    def update_profile_preferences(self, user_id: str, access_token: str, preferences: dict):
        """Update only presentation preferences for the authenticated learner under RLS."""
        allowed = {key: value for key, value in preferences.items() if key in {'display_name', 'locale', 'theme'}}
        if not allowed:
            return self.get_profile(user_id, access_token)
        result = self.user_client(access_token).table('profiles').update(allowed).eq('id', str(user_id)).execute().data
        return result[0] if result else self.get_profile(user_id, access_token)

    def get_lesson_progress(self, user_id: str, access_token: str):
        """Return only the authenticated learner's completed lesson records under RLS."""
        result = self.user_client(access_token).table('lesson_progress').select('course_id,lesson_id,completed_at').eq('user_id', str(user_id)).execute()
        return result.data or []

    def get_course_progress(self, user_id: str, access_token: str):
        """Return only the authenticated learner's aggregate course percentages under RLS."""
        result = self.user_client(access_token).table('course_progress').select('course_id,progress_percent,updated_at').eq('user_id', str(user_id)).execute()
        return result.data or []

    def complete_lesson(self, user_id: str, access_token: str, course_id: str, lesson_id: str):
        """Idempotently mark one learner-owned lesson complete under RLS."""
        result = self.user_client(access_token).table('lesson_progress').upsert({
            'user_id': str(user_id),
            'course_id': course_id,
            'lesson_id': lesson_id,
        }, on_conflict='user_id,course_id,lesson_id').execute()
        return result.data[0] if result.data else None

    def remove_lesson_completion(self, user_id: str, access_token: str, course_id: str, lesson_id: str):
        """Remove one learner-owned completion record under RLS."""
        self.user_client(access_token).table('lesson_progress').delete().eq('user_id', str(user_id)).eq('course_id', course_id).eq('lesson_id', lesson_id).execute()

    def save_course_progress(self, user_id: str, access_token: str, course_id: str, progress_percent: int):
        """Persist a calculated percentage after a lesson status changes under RLS."""
        bounded_percent = max(0, min(100, int(progress_percent)))
        result = self.user_client(access_token).table('course_progress').upsert({
            'user_id': str(user_id),
            'course_id': course_id,
            'progress_percent': bounded_percent,
        }, on_conflict='user_id,course_id').execute()
        return result.data[0] if result.data else None

    # ============ USER OPERATIONS ============
    
    def create_user(self, email: str, password: str, name: str, role: str = 'student'):
        """Create a Supabase Auth identity and its local RBAC projection."""
        try:
            response = self.client.auth.sign_up({
                'email': email,
                'password': password,
                'options': {'data': {'display_name': name}},
            })
            if not response.user:
                raise RuntimeError('Supabase Auth did not return a user')
            return self.ensure_external_user(
                auth_user_id=str(response.user.id), email=email, name=name, provider='email'
            )
        except Exception as error:
            raise RuntimeError("Failed to create user") from error

    def sign_in_with_password(self, email: str, password: str):
        """Authenticate email/password through Supabase Auth."""
        return self.client.auth.sign_in_with_password({'email': email, 'password': password})
    
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
        return self.auth_client.auth.sign_in_with_otp({'email': email, 'options': options})

    def verify_email_otp(self, email: str, code: str):
        """Verify a Supabase email OTP and return the Auth session."""
        return self.auth_client.auth.verify_otp({'email': email, 'token': code, 'type': 'email'})

    def google_login_url(self, redirect_to: str):
        """Return the Supabase-hosted Google OAuth authorization URL."""
        response = self.auth_client.auth.sign_in_with_oauth({
            'provider': 'google',
            'options': {'redirect_to': redirect_to},
        })
        return response.url

    def exchange_google_code(self, code: str):
        """Exchange the OAuth callback code for a Supabase Auth session."""
        return self.auth_client.auth.exchange_code_for_session({'auth_code': code})

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

    # ============ LEARNER-OWNED STATE ============

    def get_profile(self, user_id: str):
        response = self.client.table('profiles').select('*').eq('id', user_id).single().execute()
        return response.data

    def update_profile(self, user_id: str, changes: dict):
        allowed = {'display_name', 'locale', 'theme'}
        response = self.client.table('profiles').update(
            {key: value for key, value in changes.items() if key in allowed}
        ).eq('id', user_id).execute()
        return response.data[0] if response.data else None

    def get_learning_progress(self, user_id: str):
        courses = self.client.table('course_progress').select('*').eq('user_id', user_id).execute()
        lessons = self.client.table('lesson_progress').select('*').eq('user_id', user_id).execute()
        return {'course_progress': courses.data or [], 'lesson_progress': lessons.data or []}

    def upsert_course_progress(self, user_id: str, values: dict):
        payload = {'user_id': user_id, **values}
        response = self.client.table('course_progress').upsert(
            payload, on_conflict='user_id,course_slug'
        ).execute()
        return response.data[0] if response.data else None

    def set_lesson_progress(self, user_id: str, values: dict, completed: bool):
        query = self.client.table('lesson_progress')
        if completed:
            response = query.upsert(
                {'user_id': user_id, **values}, on_conflict='user_id,course_slug,lesson_slug'
            ).execute()
            return response.data[0] if response.data else None
        query.delete().eq('user_id', user_id).eq('course_slug', values['course_slug']).eq(
            'lesson_slug', values['lesson_slug']
        ).execute()
        return None

    def create_quiz_attempt(self, user_id: str, values: dict):
        response = self.client.table('quiz_attempts').insert({'user_id': user_id, **values}).execute()
        return response.data[0] if response.data else None

    def get_quiz_attempts(self, user_id: str):
        response = self.client.table('quiz_attempts').select('*').eq('user_id', user_id).order(
            'submitted_at', desc=True
        ).limit(100).execute()
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
