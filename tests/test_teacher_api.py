from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask

import backend.api.auth as auth_module
import backend.api.teacher as teacher_module
from backend.api.teacher import teacher_bp


SECRET = 'teacher-test-secret-with-at-least-32-bytes'


class FakeTeacherDB:
    def __init__(self):
        self.users = {
            1: {'id': 1, 'email': 'teacher@example.com', 'name': 'Teacher', 'role': 'teacher'},
            2: {'id': 2, 'email': 'student@example.com', 'name': 'Student', 'role': 'student'},
            3: {'id': 3, 'email': 'owner@example.com', 'name': 'Owner', 'role': 'owner'},
        }
        self.classes = [
            {'id': 10, 'teacher_id': 1, 'name': 'Python A', 'student_count': 12},
            {'id': 11, 'teacher_id': 3, 'name': 'Admin Class', 'student_count': 5},
        ]

    def get_user(self, user_id):
        return self.users.get(user_id)

    def get_teacher_classes(self, teacher_id):
        return [item for item in self.classes if item['teacher_id'] == teacher_id]

    def get_all_classes(self):
        return self.classes

    def get_class(self, class_id):
        return next((item for item in self.classes if item['id'] == class_id), None)


def make_token(user_id, role):
    return jwt.encode(
        {
            'user_id': user_id,
            'role': role,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        },
        SECRET,
        algorithm='HS256',
    )


def make_app(monkeypatch):
    fake_db = FakeTeacherDB()
    monkeypatch.setattr(auth_module, 'db', fake_db)
    monkeypatch.setattr(teacher_module, 'db', fake_db)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET
    app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
    return app


def auth_header(user_id, role):
    return {'Authorization': f'Bearer {make_token(user_id, role)}'}


def test_student_cannot_open_teacher_dashboard(monkeypatch):
    client = make_app(monkeypatch).test_client()

    response = client.get('/api/teacher/dashboard', headers=auth_header(2, 'student'))

    assert response.status_code == 403
    assert response.get_json()['error']['code'] == 'permission_denied'


def test_teacher_sees_own_classes_and_cannot_view_other_class(monkeypatch):
    client = make_app(monkeypatch).test_client()

    dashboard = client.get('/api/teacher/dashboard', headers=auth_header(1, 'teacher'))
    own_class = client.get('/api/teacher/classes/10/analytics', headers=auth_header(1, 'teacher'))
    other_class = client.get('/api/teacher/classes/11/analytics', headers=auth_header(1, 'teacher'))

    assert dashboard.status_code == 200
    assert dashboard.get_json()['total_classes'] == 1
    assert own_class.status_code == 200
    assert own_class.get_json()['analytics']['total_students'] == 12
    assert other_class.status_code == 403


def test_owner_sees_all_teacher_classes(monkeypatch):
    client = make_app(monkeypatch).test_client()

    response = client.get('/api/teacher/dashboard', headers=auth_header(3, 'owner'))

    assert response.status_code == 200
    assert response.get_json()['total_classes'] == 2
    assert response.get_json()['total_students'] == 17
