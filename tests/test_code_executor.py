import json

import backend.services.code_executor as code_executor_module
from backend.services.code_executor import CodeExecutor


class FakeContainers:
    def __init__(self):
        self.kwargs = None

    def run(self, *args, **kwargs):
        self.kwargs = kwargs
        return json.dumps({'status': 'accepted', 'passed': True}).encode()


class FakeClient:
    def __init__(self):
        self.containers = FakeContainers()


def executor_with_fake_client():
    executor = object.__new__(CodeExecutor)
    executor.image_name = 'code-sandbox:latest'
    executor.client = FakeClient()
    return executor


def test_rejects_unsupported_language_before_docker_call():
    executor = executor_with_fake_client()

    result = executor.execute_code('print(1)', 'ruby')

    assert result['status'] == 'error'
    assert 'Unsupported language' in result['error']
    assert executor.client.containers.kwargs is None


def test_rejects_unbounded_resources():
    executor = executor_with_fake_client()

    result = executor.execute_code('print(1)', 'python', timeout=60, memory_limit_mb=1024)

    assert result['status'] == 'error'
    assert 'Timeout must be between' in result['error']
    assert executor.client.containers.kwargs is None


def test_secure_container_options_are_applied():
    executor = executor_with_fake_client()

    result = executor.execute_code('print(1)', 'python')

    assert result['status'] == 'accepted'
    options = executor.client.containers.kwargs
    assert options['network_disabled'] is True
    assert options['cap_drop'] == ['ALL']
    assert options['read_only'] is True
    assert options['pids_limit'] == 64


def test_rejects_more_than_maximum_test_cases():
    executor = executor_with_fake_client()

    result = executor.execute_test_cases('print(1)', 'python', [{}] * 101)

    assert result['status'] == 'error'
    assert 'Test case count exceeds' in result['error']


def test_remote_sandbox_path_uses_internal_http_service(monkeypatch):
    executor = executor_with_fake_client()
    calls = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {'status': 'completed', 'passed': True}

    def fake_post(url, **kwargs):
        calls['url'] = url
        calls['kwargs'] = kwargs
        return FakeResponse()

    monkeypatch.setenv('SANDBOX_URL', 'http://sandbox:8080')
    monkeypatch.setenv('SANDBOX_TOKEN', 'sandbox-secret')
    monkeypatch.setattr(code_executor_module.requests, 'post', fake_post)

    result = executor.execute_code('print(1)', 'python', expected_output='1')

    assert result['passed'] is True
    assert calls['url'] == 'http://sandbox:8080/execute'
    assert calls['kwargs']['headers']['X-Sandbox-Token'] == 'sandbox-secret'
    assert calls['kwargs']['json']['expected_output'] == '1'
    assert executor.client.containers.kwargs is None


def test_host_docker_execution_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv('SANDBOX_URL', raising=False)
    monkeypatch.delenv('ALLOW_LOCAL_DOCKER_SANDBOX', raising=False)
    executor = CodeExecutor()

    result = executor.execute_code('print(1)', 'python')

    assert result['status'] == 'error'
    assert result['error'] == 'Sandbox execution is temporarily unavailable.'
