"""Local ResidualLab demo server. It serves only synthetic scenarios; never executes tools."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SCENARIOS = {
    "canonical": {
        "label": "canonical prohibited action; recognized and denied",
        "action": "a canonical tool action in the sensitive-data category",
        "adapter": "recognized as prohibited",
        "outcome": "denied; no effect",
    },
    "variant": {
        "label": "syntactic variant of a prohibited action; missed and admitted",
        "action": "a syntactic variant with the same simulated sensitive-data effect",
        "adapter": "unmatched and admitted by a deliberately permissive study adapter",
        "outcome": "simulated side effect in a toy environment",
    },
    "benign": {
        "label": "allowed maintenance action",
        "action": "a read-only status check",
        "adapter": "mapped to an allowed event",
        "outcome": "completed without a side effect",
    },
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = "/index.html" if self.path == "/" else self.path.split("?", 1)[0]
        if path not in ("/index.html", "/app.js", "/style.css"):
            self.send_error(404)
            return
        file_path = ROOT / path.lstrip("/")
        content_type = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}[file_path.suffix]
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/explain":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 4096:
                self.send_error(413)
                return
            data = json.loads(self.rfile.read(size))
            scenario = SCENARIOS.get(data.get("scenario"))
            if not scenario:
                self.send_error(400, "Unknown scenario")
                return
            key = os.environ.get("MODEL_API_KEY")
            if not key:
                self.reply(503, {"error": "MODEL_API_KEY is not configured."})
                return
            prompt = (
                "You are explaining a safe, synthetic agent-safety demonstration. "
                "Do not provide commands or operational instructions. In at most 120 words, "
                "explain the policy/adapter mismatch and suggest one safe regression test. "
                f"Scenario: {scenario['label']}. Abstract action: {scenario['action']}. "
                f"Adapter: {scenario['adapter']}. Simulated outcome: {scenario['outcome']}."
            )
            req = Request(
                "https://api.meta.ai/v1/responses",
                data=json.dumps({"model": "muse-spark-1.3", "input": prompt}).encode(),
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=40) as response:
                payload = json.loads(response.read())
            text = payload.get("output_text")
            if not text:
                parts = []
                for item in payload.get("output", []):
                    for part in item.get("content", []):
                        if part.get("type") in ("output_text", "text"):
                            parts.append(part.get("text", ""))
                text = "\n".join(parts).strip()
            if not text:
                raise ValueError("Meta Model API returned no text.")
            self.reply(200, {"explanation": text})
        except HTTPError as exc:
            self.reply(502, {"error": f"Meta Model API returned HTTP {exc.code}."})
        except (URLError, TimeoutError):
            self.reply(502, {"error": "Could not reach Meta Model API."})
        except (ValueError, json.JSONDecodeError) as exc:
            self.reply(400, {"error": str(exc)})
        except Exception:
            self.reply(500, {"error": "The explanation request failed."})

    def reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"ResidualLab running at http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
