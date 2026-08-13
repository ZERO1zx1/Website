from datetime import datetime, timezone

import jwt
from flask import Flask
from werkzeug.security import generate_password_hash

import backend.api.auth as auth_module
from backend.api.auth import auth_bp


class FakeDB:
    def __init__(self):
        self.users = {
            1: {
                'id': 1,
                'email': 'owner@example.com',
                'name': 'Owner',
                'password_hash': generate_password_hash('OwnerPass123'),
                'role': 'owner',
                'requested_role': None,
                'teacher_approval_status': 'approved',
            }
        }

    def get_user_by_email(self, email):
        return next((user for user in self.users.values() if user['email'] == email), None)

    def get_user(self, user_id):
        return self.users.get(user_id)

    def create_user(self, email, password, name, role='student'):
        user = {
            'id': max(self.users) + 1,
            'email': email,
            'name': name,
            'password_hash': generate_password_hash(password),
            'role': role,
            'requested_role': None,
            'teacher_approval_status': 'approved',
        }
        self.users[user['id']] = user
        return user

    def update_user(self, user_id, data):
        self.users[user_id].update(data)
        return self.users[user_id]

    def get_pending_teacher_requests(self):
        return []


def make_app(monkeypatch):
    fake_db = FakeDB()
    monkeypatch.setattr(auth_module, 'db', fake_db)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key-with-at-least-32-bytes'
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    return app, fake_db


def test_register_hashes_password_and_ignores_client_role(monkeypatch):
    app, fake_db = make_app(monkeypatch)
    client = app.test_client()

    response = client.post('/api/auth/register', json={
        'email': 'student@example.com',
        'name': 'Student',
        'password': 'StudentPass123',
        'role': 'owner',
    })

    assert response.status_code == 201
    created = fake_db.get_user_by_email('student@example.com')
    assert created['role'] == 'student'
    assert 'password' not in created
    assert created['password_hash'] != 'StudentPass123'


def test_login_returns_jwt_and_rejects_wrong_password(monkeypatch):
    app, _ = make_app(monkeypatch)
    client = app.test_client()

    success = client.post('/api/auth/login', json={
        'email': 'owner@example.com',
        'password': 'OwnerPass123',
    })
    assert success.status_code == 200
    token = success.get_json()['token']
    payload = jwt.decode(token, 'test-secret-key-with-at-least-32-bytes', algorithms=['HS256'])
    assert payload['role'] == 'owner'
    assert payload['exp'] > datetime.now(timezone.utc).timestamp()

    failure = client.post('/api/auth/login', json={
        'email': 'owner@example.com',
        'password': 'wrong-password',
    })
    assert failure.status_code == 401
    assert failure.get_json()['error']['code'] == 'invalid_credentials'


def test_owner_can_manage_role_and_mongolian_error_is_stable(monkeypatch):
    app, fake_db = make_app(monkeypatch)
    client = app.test_client()
    token_response = client.post('/api/auth/login', json={
        'email': 'owner@example.com',
        'password': 'OwnerPass123',
    })
    token = token_response.get_json()['token']
    fake_db.users[2] = {
        'id': 2,
        'email': 'student2@example.com',
        'name': 'Student 2',
        'password_hash': generate_password_hash('StudentPass123'),
        'role': 'student',
        'requested_role': None,
        'teacher_approval_status': 'approved',
    }

    updated = client.patch(
        '/api/auth/users/2/role',
        headers={'Authorization': f'Bearer {token}', 'Accept-Language': 'mn-MN'},
        json={'role': 'teacher'},
    )
    assert updated.status_code == 200
    assert fake_db.users[2]['role'] == 'teacher'

    invalid = client.patch(
        '/api/auth/users/2/role',
        headers={'Authorization': f'Bearer {token}', 'Accept-Language': 'mn-MN'},
        json={'role': 'superuser'},
    )
    assert invalid.status_code == 400
    assert invalid.get_json()['error']['message_mn'] == 'Хүссэн үүрэг буруу байна.'
