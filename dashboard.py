"""Live dashboard for the catalysis AutoResearch harness (FIXED; stdlib only).

    uv run dashboard.py            # then open http://localhost:8000

Shows the current model fit (refreshed each train.py run) and the AutoResearch
progress from results.tsv. The page auto-refreshes every 2 seconds.
"""
from __future__ import annotations

import argparse
import http.server
import pathlib
import socketserver

import prepare

HERE = pathlib.Path(__file__).resolve().parent
DASH = prepare.DASH_DIR
RESULTS = HERE / "results.tsv"

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="2">
<title>Catalysis AutoResearch - live</title>
<style>
 body{{font-family:system-ui,sans-serif;margin:24px;max-width:900px}}
 img{{max-width:100%;border:1px solid #ccc}}
 table{{border-collapse:collapse;font-size:13px}}
 h2{{margin-top:28px}} .note{{color:#888}}
</style></head><body>
<h1>Catalysis AutoResearch - live</h1>
<h2>Current model fit</h2>{fit}
<h2>AutoResearch progress</h2>{progress}{table}
<p class="note">auto-refreshing every 2s</p>
</body></html>"""


def _img(name):
    f = DASH / name
    if f.exists():
        return f'<img src="/{name}?t={f.stat().st_mtime}">'
    return "<p><em>waiting for the first run...</em></p>"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/fit.png", "/progress.png"):
            f = DASH / path.lstrip("/")
            if f.exists():
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(f.read_bytes())
            else:
                self.send_error(404)
            return
        # Regenerate progress.png only when the ledger is newer (cheap + fresh).
        try:
            pp = DASH / "progress.png"
            if RESULTS.exists() and (
                not pp.exists() or pp.stat().st_mtime < RESULTS.stat().st_mtime
            ):
                prepare.save_progress_plot(RESULTS, pp)
        except Exception:
            pass
        html = PAGE.format(
            fit=_img("fit.png"),
            progress=_img("progress.png"),
            table=prepare.results_table_html(RESULTS),
        )
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    DASH.mkdir(exist_ok=True)
    with socketserver.TCPServer(("127.0.0.1", args.port), Handler) as httpd:
        print(f"dashboard: http://localhost:{args.port}  (Ctrl-C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
