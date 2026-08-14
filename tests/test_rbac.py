from flask import Flask

from backend.rbac import ROLE_PERMISSIONS, error_response, has_permission, role_label


def test_role_matrix_contains_owner_and_expected_grants():
    assert role_label('owner', 'mn') == 'Эзэмшигч'
    assert role_label('teacher', 'mn') == 'Багш'
    assert 'owner.manage' in ROLE_PERMISSIONS['owner']
    assert 'owner.manage' not in ROLE_PERMISSIONS['admin']
    assert has_permission({'role': 'teacher'}, 'analytics.read')
    assert has_permission({'role': 'student'}, 'student.dashboard.read')
    assert not has_permission({'role': 'student'}, 'teachers.approve')


def test_permission_error_uses_mongolian_message_for_mn_locale():
    app = Flask(__name__)
    with app.test_request_context('/', headers={'Accept-Language': 'mn-MN'}):
        payload, status = error_response(
            'permission_denied',
            'You do not have permission to perform this action.',
            'Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна.',
            403,
        )

    assert status == 403
    assert payload['error']['code'] == 'permission_denied'
    assert payload['error']['message'] == 'Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна.'
    assert payload['error']['message_mn'] == 'Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна.'
