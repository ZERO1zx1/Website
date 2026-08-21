import pytest

from app import create_app


@pytest.fixture()
def frontend_app(monkeypatch):
    monkeypatch.setenv('FRONTEND_ONLY', 'true')
    return create_app()


def test_frontend_shell_renders_without_backend_credentials(frontend_app):
    client = frontend_app.test_client()

    response = client.get('/')

    assert response.status_code == 200
    assert b'CodeCraft Academy' in response.data
    assert 'Код бичихийг'.encode() in response.data
    assert b'id="main-content"' in response.data
    assert b'class="hero-section' in response.data
    assert b'frontend/static' not in response.data
    assert b'aria-live="polite"' in response.data


def test_frontend_static_assets_are_available(frontend_app):
    client = frontend_app.test_client()

    css_response = client.get('/static/css/style.css')
    adapter_response = client.get('/static/js/adapters/api-adapter.js')
    js_response = client.get('/static/js/app.js')

    assert css_response.status_code == 200
    assert b'--ink:' in css_response.data
    assert adapter_response.status_code == 200
    assert b'codehavenApiAdapter' in adapter_response.data
    assert js_response.status_code == 200
    assert b'CODECRAFT_CONFIG' in js_response.data
    assert b"credentials: 'same-origin'" in js_response.data
    assert b'codecraft_token' not in js_response.data


def test_frontend_only_mode_keeps_health_endpoint(frontend_app):
    client = frontend_app.test_client()

    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'
