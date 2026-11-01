"""Run the NiyamGate local demonstration: python app.py"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
from urllib.parse import urlparse

from guard import SCENARIOS, run_scenario

ROOT = Path(__file__).resolve().parent


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send((ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/api/scenarios":
            body = [{"id": key, "title": value["title"], "summary": value["summary"]}
                    for key, value in SCENARIOS.items()]
            self._send(json.dumps(body).encode(), "application/json; charset=utf-8")
        else:
            self._send(b"Not found", "text/plain; charset=utf-8", 404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/run":
            self._send(b"Not found", "text/plain; charset=utf-8", 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 16384:
                raise ValueError("Request must be between 1 and 16384 bytes.")
            payload = json.loads(self.rfile.read(length))
            result = run_scenario(str(payload.get("scenario", "")))
            self._send(json.dumps(result).encode(), "application/json; charset=utf-8")
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(json.dumps({"error": str(exc)}).encode(), "application/json; charset=utf-8", 400)
        except KeyError:
            self._send(b'{"error":"Unknown scenario."}', "application/json; charset=utf-8", 404)

    def log_message(self, _format: str, *_args: object) -> None:
        return


if __name__ == "__main__":
    print("NiyamGate is local at http://127.0.0.1:8765 (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()

