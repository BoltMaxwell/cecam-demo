"""Presenter dashboard server: built SPA + JSON API (stdlib only).

    uv run server.py            # then open http://localhost:8000

Serves frontend/dist/ (the built React SPA) plus:
    /api/state    current model fit    (.dash/state.json, written by train.py)
    /api/ledger   the experiment ledger (results.tsv)

Runtime needs only Python; node is used once, at build time (see frontend/).
"""
from __future__ import annotations

import argparse
import http.server
import json
import math
import pathlib

import prepare

HERE = pathlib.Path(__file__).resolve().parent
DIST = HERE / "frontend" / "dist"
RESULTS = HERE / "results.tsv"
STATE = prepare.DASH_DIR / "state.json"


def _finite_or_none(value):
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def state_payload(state_path):
    """The state JSON with ready=True, or {"ready": False} if absent/corrupt."""
    p = pathlib.Path(state_path)
    try:
        state = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"ready": False}
    state["ready"] = True
    return state


def ledger_payload(results_tsv):
    """results.tsv as strictly-valid JSON rows (iter derived, NaN -> null)."""
    rows = []
    for i, r in enumerate(prepare._read_ledger(results_tsv)):
        rows.append({
            "iter": i,
            "commit": r.get("commit", ""),
            "elbo": _finite_or_none(r.get("elbo")),
            "mass_residual": _finite_or_none(r.get("mass_residual")),
            "mass_gate": r.get("mass_gate") or None,
            "status": r.get("status", ""),
            "description": r.get("description", ""),
        })
    return {"rows": rows}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/state":
            return self._json(state_payload(STATE))
        if path == "/api/ledger":
            return self._json(ledger_payload(RESULTS))
        super().do_GET()

    def _json(self, payload):
        body = json.dumps(payload, allow_nan=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(port):
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    if not (DIST / "index.html").exists():
        print("note: frontend/dist/index.html missing — run `cd frontend && "
              "npm run build` (the /api endpoints still work, e.g. for npm run dev)")
    try:
        httpd = make_server(args.port)
    except OSError as e:
        raise SystemExit(f"port {args.port} is busy ({e}); try: uv run server.py --port 8001")
    with httpd:
        print(f"dashboard: http://localhost:{args.port}  (Ctrl-C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
