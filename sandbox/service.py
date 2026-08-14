"""Internal HTTP service for isolated code execution.

The service is intentionally reachable only from the application network. In
production it requires a non-empty shared token before it starts and verifies
that token on every execution request.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os

try:
    from .runner import CodeRunner
except ImportError:  # pragma: no cover - direct container execution
    from runner import CodeRunner


MAX_REQUEST_BYTES = 120_000


def _token_is_required() -> bool:
    configured = os.getenv("SANDBOX_REQUIRE_TOKEN")
    if configured is not None:
        return configured.strip().lower() in {"1", "true", "yes", "on"}
    # Fail closed. A no-token development/test service must explicitly opt in.
    allow_insecure = os.getenv("SANDBOX_ALLOW_INSECURE", "false").strip().lower()
    return allow_insecure not in {"1", "true", "yes", "on"}


def _configured_token() -> str:
    return os.getenv("SANDBOX_TOKEN", "").strip()


class SandboxHandler(BaseHTTPRequestHandler):
    server_version = "CodehavenSandbox/1.0"

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            self._send(200, {"status": "healthy", "execution_auth_required": _token_is_required()})
            return
        self._send(404, {"error": "Not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/execute":
            self._send(404, {"error": "Not found"})
            return

        expected_token = _configured_token()
        if not expected_token and _token_is_required():
            self._send(503, {"error": "Sandbox authentication is not configured"})
            return
        if expected_token and self.headers.get("X-Sandbox-Token") != expected_token:
            self._send(403, {"error": "Forbidden"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                self._send(400, {"error": "Invalid request size"})
                return
            payload = json.loads(self.rfile.read(content_length))
            code = payload.get("code")
            language = payload.get("language", "python")
            timeout = int(payload.get("timeout", 5))
            memory_limit = int(payload.get("memory_limit_mb", 256))
            if not isinstance(code, str) or not code.strip():
                self._send(400, {"error": "Code must be a non-empty string"})
                return
            if timeout < 1 or timeout > 30 or memory_limit < 32 or memory_limit > 512:
                self._send(400, {"error": "Execution limits are outside the allowed range"})
                return
            runner = CodeRunner(timeout=timeout, memory_limit_mb=memory_limit)
            result = runner.run_test_case(
                code=code,
                language=language,
                test_input=str(payload.get("input", "")),
                expected_output=str(payload.get("expected_output", "")),
            )
            self._send(200, result)
        except (ValueError, TypeError, json.JSONDecodeError):
            self._send(400, {"error": "Invalid execution request"})
        except Exception:  # pragma: no cover - final service guard
            self._send(500, {"error": "Sandbox execution failed"})

    def log_message(self, format, *args):  # noqa: A003
        return


def main() -> None:
    if _token_is_required() and not _configured_token():
        raise RuntimeError("SANDBOX_TOKEN must be set when sandbox token authentication is required")
    port = int(os.getenv("SANDBOX_PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), SandboxHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
