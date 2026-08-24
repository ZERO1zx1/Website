"""Internal HTTP bridge for the isolated code runner.

The service is intended to be reachable only on the compose internal network.
It does not expose the sandbox directly to the public host.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from runner import CodeRunner


SUPPORTED_LANGUAGES = {"python", "javascript"}
MAX_CODE_LENGTH = 100_000
MIN_TIMEOUT = 1
MAX_TIMEOUT = 15
MIN_MEMORY_MB = 64
MAX_MEMORY_MB = 512


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
            self._send(200, {"status": "healthy"})
            return
        self._send(404, {"error": "Not found"})

    def do_POST(self):  # noqa: N802
        if self.path != "/execute":
            self._send(404, {"error": "Not found"})
            return

        expected_token = os.getenv("SANDBOX_TOKEN", "")
        if expected_token and self.headers.get("X-Sandbox-Token") != expected_token:
            self._send(403, {"error": "Forbidden"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 120_000:
                self._send(400, {"error": "Invalid request size"})
                return
            payload = json.loads(self.rfile.read(content_length))
            code = payload.get("code")
            language = str(payload.get("language", "python")).lower()
            timeout = int(payload.get("timeout", 5))
            memory_limit = int(payload.get("memory_limit_mb", 256))
            if not isinstance(code, str) or not code.strip():
                self._send(400, {"error": "Code must be a non-empty string"})
                return
            if len(code) > MAX_CODE_LENGTH:
                self._send(400, {"error": "Code exceeds the maximum length"})
                return
            if language not in SUPPORTED_LANGUAGES:
                self._send(400, {"error": "Unsupported sandbox language"})
                return
            if not MIN_TIMEOUT <= timeout <= MAX_TIMEOUT:
                self._send(400, {"error": "Timeout is outside the allowed range"})
                return
            if not MIN_MEMORY_MB <= memory_limit <= MAX_MEMORY_MB:
                self._send(400, {"error": "Memory limit is outside the allowed range"})
                return
            runner = CodeRunner(timeout=timeout, memory_limit_mb=memory_limit)
            result = runner.run_test_case(
                code=code,
                language=language,
                test_input=str(payload.get("input", "")),
                expected_output=str(payload.get("expected_output", "")),
            )
            self._send(200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._send(400, {"error": f"Invalid execution request: {error}"})
        except Exception:  # pragma: no cover - final service guard
            self._send(500, {"error": "Sandbox execution failed"})

    def log_message(self, format, *args):  # noqa: A003
        return


def main() -> None:
    port = int(os.getenv("SANDBOX_PORT", "8080"))
    server = ThreadingHTTPServer((os.getenv("SANDBOX_HOST", "0.0.0.0"), port), SandboxHandler)  # nosec B104
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
