"""Private loopback-only HTTP interface; no accounts and no external calls."""
import argparse
import json
import secrets
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from . import __version__
from .engine import PRESETS
from .jobs import JobStore, JobWorker
from .probe import MediaError, check_executables, inspect_media

WEB = Path(__file__).resolve().parent.parent / "web"


def make_handler(store, worker, token):
    class Handler(BaseHTTPRequestHandler):
        server_version = "MediaForge/0.1"
        def log_message(self, format, *args):
            # Don't log submitted local paths, URLs, or media names.
            pass

        def send_bytes(self, code, content, content_type="application/json; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(content)

        def send_json(self, code, obj):
            self.send_bytes(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

        def do_GET(self):
            url = urllib.parse.urlsplit(self.path)
            if url.path == "/api/health":
                return self.send_json(200, {"version": __version__, "executables": check_executables(), "prototype": True})
            if url.path == "/api/jobs":
                return self.send_json(200, {"jobs": store.list()})
            if url.path == "/api/presets":
                return self.send_json(200, {"presets": PRESETS})
            if url.path == "/api/session":
                return self.send_json(200, {"token": token})
            if url.path in ("/", "/index.html", "/app.js", "/style.css"):
                path = WEB / ("index.html" if url.path == "/" else url.path.lstrip("/"))
                if path.exists():
                    mimetype = "text/html; charset=utf-8" if path.suffix == ".html" else "text/javascript; charset=utf-8" if path.suffix == ".js" else "text/css; charset=utf-8"
                    return self.send_bytes(200, path.read_bytes(), mimetype)
            return self.send_json(404, {"error": "Not found"})

        def do_POST(self):
            origin = self.headers.get("Origin")
            if origin and origin != f"http://127.0.0.1:{self.server.server_port}":
                return self.send_json(403, {"error": "Cross-origin requests are not accepted"})
            if self.headers.get("X-Media-Forge-Token") != token:
                return self.send_json(403, {"error": "Invalid local session token"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size < 0 or size > 32 * 1024:
                    return self.send_json(413, {"error": "Request too large"})
                body = json.loads(self.rfile.read(size)) if size else {}
                if not isinstance(body, dict):
                    raise ValueError("Expected JSON object")
                if self.path == "/api/scan":
                    return self.send_json(200, inspect_media(body.get("path", "")))
                if self.path == "/api/jobs":
                    return self.send_json(201, store.submit(body))
                if self.path.startswith("/api/jobs/") and self.path.endswith("/cancel"):
                    id_ = self.path.split("/")[3]
                    if worker.cancel(id_):
                        return self.send_json(200, {"accepted": True})
                    return self.send_json(409, {"error": "Job not cancelable"})
                return self.send_json(404, {"error": "Not found"})
            except (MediaError, ValueError, json.JSONDecodeError, TypeError) as exc:
                return self.send_json(400, {"error": str(exc)})
            except Exception:
                return self.send_json(500, {"error": "Unexpected server error"})

    return Handler


def create_server(db_path: Path, port=8765):
    store = JobStore(db_path)
    worker = JobWorker(store, db_path.parent / "logs")
    token = secrets.token_urlsafe(32)
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(store, worker, token))
    worker.start()
    return server, worker


def main():
    p = argparse.ArgumentParser(description="GoreeCloud Media Forge prototype")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--db", type=Path, default=Path.home() / ".local" / "state" / "media-forge" / "jobs.sqlite3")
    p.add_argument("--no-browser", action="store_true")
    args = p.parse_args()
    server, worker = create_server(args.db, args.port)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Media Forge {__version__} running at {url} (local device only)", flush=True)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        worker.stop()
        server.server_close()


if __name__ == "__main__":
    main()
