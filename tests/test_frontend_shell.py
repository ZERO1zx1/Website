import pytest

from app import create_app


@pytest.fixture()
def frontend_app(monkeypatch):
    monkeypatch.setenv('FRONTEND_ONLY', 'true')
    return create_app()


def test_workspace_alias_renders_canonical_dashboard_without_backend_credentials(frontend_app):
    client = frontend_app.test_client()

    response = client.get('/workspace')

    assert response.status_code == 200
    assert b'Codehaven' in response.data
    assert b'Keep your momentum' in response.data
    assert b'id="dashboard-view"' in response.data
    assert b'id="activity-chart"' in response.data
    assert b'id="dashboard-report-summary"' in response.data
    assert b'frontend/static' not in response.data
    assert b'js/app.js' in response.data
    assert b'id="course-grid"' not in response.data


def test_root_uses_public_landing_page(frontend_app):
    response = frontend_app.test_client().get('/')

    assert response.status_code == 200
    assert b'Start learning free' in response.data
    assert b'class="marketing-hero"' in response.data
    assert b'Keep your momentum' not in response.data


def test_frontend_static_assets_are_available(frontend_app):
    client = frontend_app.test_client()

    css_response = client.get('/static/css/style.css')
    adapter_response = client.get('/static/js/adapters/api-adapter.js')
    js_response = client.get('/static/js/app.js')

    assert css_response.status_code == 200
    assert b'--color-action-primary' in css_response.data
    assert adapter_response.status_code == 200
    assert b'codehavenApiAdapter' in adapter_response.data
    assert js_response.status_code == 200
    assert b'mockAdapter' in js_response.data
    assert b'No preset learner is shipped' in js_response.data


def test_frontend_only_mode_keeps_health_endpoint(frontend_app):
    response = frontend_app.test_client().get('/api/health')

    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'
