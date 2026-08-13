import os

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
    assert b'Codehaven' in response.data
    assert b'Keep your momentum' in response.data
    assert b'frontend/static' not in response.data


def test_frontend_static_assets_are_available(frontend_app):
    client = frontend_app.test_client()

    css_response = client.get('/static/css/style.css')
    js_response = client.get('/static/js/app.js')

    assert css_response.status_code == 200
    assert b'--color-action-primary' in css_response.data
    assert js_response.status_code == 200
    assert b'mockAdapter' in js_response.data


def test_frontend_only_mode_keeps_health_endpoint(frontend_app):
    client = frontend_app.test_client()

    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'
