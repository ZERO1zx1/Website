from types import SimpleNamespace

import jwt
from flask import Flask

import backend.api.auth as auth_module
from backend.api.auth import auth_bp


SECRET = 'provider-test-secret-with-at-least-32-bytes'


class FakeProviderDB:
    def __init__(self):
        self.otp_requests = []
        self.users = {
            7: {
                'id': 7,
                'email': 'student@gmail.com',
                'name': 'Student',
                'role': 'student',
                'requested_role': None,
                'teacher_approval_status': 'approved',
            }
        }

    def request_email_otp(self, email, redirect_to=None):
        self.otp_requests.append((email, redirect_to))
        return SimpleNamespace(message_id='message-1')

    def verify_email_otp(self, email, code):
        assert email == 'student@gmail.com'
        assert code == '123456'
        return SimpleNamespace(
            user=SimpleNamespace(
                id='supabase-user-7',
                email=email,
                user_metadata={'full_name': 'Student'},
            )
        )

    def ensure_external_user(self, **kwargs):
        assert kwargs['provider'] in {'email', 'google'}
        user = self.users[7].copy()
        user['auth_user_id'] = kwargs['auth_user_id']
        user['auth_provider'] = kwargs['provider']
        return user

    def google_login_url(self, redirect_to):
        return f'https://accounts.google.com/o/oauth2/auth?redirect_uri={redirect_to}'

    def exchange_google_code(self, code):
        assert code == 'oauth-code'
        return self.verify_email_otp('student@gmail.com', '123456')


def make_app(monkeypatch):
    fake_db = FakeProviderDB()
    monkeypatch.setattr(auth_module, 'db', fake_db)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET
    app.config['TESTING'] = True
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    return app, fake_db


def test_otp_request_validates_email_and_delegates(monkeypatch):
    app, fake_db = make_app(monkeypatch)
    client = app.test_client()

    response = client.post('/api/auth/otp/request', json={'email': 'student@gmail.com'})

    assert response.status_code == 200
    assert fake_db.otp_requests == [('student@gmail.com', None)]
    assert 'six-digit' not in response.get_json()['message_mn']


def test_otp_verify_returns_app_jwt_and_preserves_student_role(monkeypatch):
    app, _ = make_app(monkeypatch)
    client = app.test_client()

    response = client.post('/api/auth/otp/verify', json={
        'email': 'student@gmail.com',
        'code': '123456',
    })

    assert response.status_code == 200
    payload = response.get_json()
    claims = jwt.decode(payload['token'], SECRET, algorithms=['HS256'])
    assert claims['user_id'] == 7
    assert claims['role'] == 'student'
    assert payload['user']['role'] == 'student'


def test_google_start_returns_provider_url(monkeypatch):
    app, _ = make_app(monkeypatch)
    client = app.test_client()

    response = client.get('/api/auth/google/start')

    assert response.status_code == 200
    assert response.get_json()['url'].startswith('https://accounts.google.com/')


def test_google_callback_exchanges_code_and_redirects_with_app_token(monkeypatch):
    app, _ = make_app(monkeypatch)
    app.config['SERVER_NAME'] = 'localhost'
    client = app.test_client()

    response = client.get('/api/auth/google/callback?code=oauth-code')

    assert response.status_code == 302
    assert 'auth_token=' in response.headers['Location']
    assert 'auth_provider=google' in response.headers['Location']
