from datetime import datetime, timedelta, timezone

import pytest

import backend.email_service as email_service


def test_issue_and_verify_email_code_is_one_time(monkeypatch):
    sent = {}

    def fake_send(recipient, code, expires_minutes):
        sent.update(recipient=recipient, code=code, expires_minutes=expires_minutes)

    monkeypatch.setattr(email_service, '_send_message', fake_send)
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key-with-at-least-32-bytes')

    challenge = email_service.issue_email_code('Student@Gmail.com')
    assert sent['recipient'] == 'student@gmail.com'
    assert len(sent['code']) == 6
    assert sent['code'].isdigit()
    assert sent['expires_minutes'] == 10

    email_service.verify_email_code('student@gmail.com', challenge, sent['code'])
    with pytest.raises(email_service.InvalidEmailCode):
        email_service.verify_email_code('student@gmail.com', challenge, sent['code'])


def test_invalid_code_is_limited_and_challenge_expires(monkeypatch):
    sent = {}
    monkeypatch.setattr(email_service, '_send_message', lambda recipient, code, expires_minutes: sent.update(code=code))
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key-with-at-least-32-bytes')

    challenge = email_service.issue_email_code('student@gmail.com')
    for _ in range(4):
        with pytest.raises(email_service.InvalidEmailCode):
            email_service.verify_email_code('student@gmail.com', challenge, '000000')
    with pytest.raises(email_service.InvalidEmailCode):
        email_service.verify_email_code('student@gmail.com', challenge, '000000')
    with pytest.raises(email_service.InvalidEmailCode):
        email_service.verify_email_code('student@gmail.com', challenge, sent['code'])


def test_expired_challenge_is_rejected(monkeypatch):
    sent = {}
    monkeypatch.setattr(email_service, '_send_message', lambda recipient, code, expires_minutes: sent.update(code=code))
    monkeypatch.setenv('SECRET_KEY', 'test-secret-key-with-at-least-32-bytes')

    challenge = email_service.issue_email_code('student@gmail.com')
    with email_service._lock:
        email_service._challenges[challenge].expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    with pytest.raises(email_service.InvalidEmailCode):
        email_service.verify_email_code('student@gmail.com', challenge, sent['code'])
