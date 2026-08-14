import pytest

from app import create_app


def test_frontend_only_mode_does_not_require_supabase(monkeypatch):
    monkeypatch.setenv('FRONTEND_ONLY', 'true')
    monkeypatch.delenv('SUPABASE_URL', raising=False)
    monkeypatch.delenv('SUPABASE_KEY', raising=False)

    app = create_app()

    assert app.config['FRONTEND_ONLY'] is True
    assert app.test_client().get('/').status_code == 200


def test_frontend_only_readiness_is_ready(monkeypatch):
    monkeypatch.setenv('FRONTEND_ONLY', 'true')
    app = create_app()

    response = app.test_client().get('/api/ready')

    assert response.status_code == 200
    assert response.get_json()['mode'] == 'frontend-only'


def test_normal_backend_readiness_reports_missing_configuration(monkeypatch):
    monkeypatch.setenv('FRONTEND_ONLY', 'false')
    monkeypatch.delenv('SUPABASE_URL', raising=False)
    monkeypatch.delenv('SUPABASE_KEY', raising=False)
    monkeypatch.setenv('SECRET_KEY', 'test-secret-that-is-long-enough-for-the-test')
    monkeypatch.setenv('SUBMISSION_QUEUE_MODE', 'thread')
    monkeypatch.setenv('LOCAL_DB', 'false')
    monkeypatch.delenv('SANDBOX_URL', raising=False)

    response = create_app().test_client().get('/api/ready')

    assert response.status_code == 503
    assert 'SUPABASE_URL' in response.get_json()['missing']


def test_normal_backend_mode_registers_user_loader(monkeypatch):
    monkeypatch.setenv('FRONTEND_ONLY', 'false')
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_KEY', 'test-key')
    monkeypatch.setenv('SECRET_KEY', 'test-secret-that-is-long-enough-for-the-test')

    app = create_app()

    assert app.config['FRONTEND_ONLY'] is False
    assert app.login_manager.user_callback is not None
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert 'Content-Security-Policy' in response.headers


def test_production_requires_explicit_secret(monkeypatch):
    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.delenv('SECRET_KEY', raising=False)

    with pytest.raises(RuntimeError, match='SECRET_KEY'):
        create_app()


def test_cors_origins_are_explicit(monkeypatch):
    monkeypatch.setenv('CORS_ORIGINS', 'https://example.com, https://admin.example.com')
    app = create_app()

    assert app.config['CORS_ORIGINS'] == ['https://example.com', 'https://admin.example.com']
