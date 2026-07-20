"""Live dashboard for the catalysis AutoResearch harness (FIXED; stdlib only).

    uv run dashboard.py            # then open http://localhost:8000

Shows the current model fit (refreshed each train.py run) and the AutoResearch
progress from results.tsv. The page auto-refreshes every 5 seconds.
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
<meta http-equiv="refresh" content="5">
<title>Catalysis AutoResearch — live</title>
<style>
 :root{{ --gold:#cfb991; --ink:#1f2933; --muted:#6b7580; --border:#e3e7eb; --bg:#f4f6f8; }}
 *{{ box-sizing:border-box; }}
 body{{ margin:0; background:var(--bg); color:var(--ink);
        font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
 header{{ background:#fff; border-top:6px solid var(--gold); border-bottom:1px solid var(--border);
          padding:14px 24px; display:flex; align-items:baseline; gap:14px; }}
 header h1{{ margin:0; font-size:1.2rem; }}
 header .live{{ font-size:.72rem; color:#fff; background:#2e7d32; border-radius:999px;
               padding:2px 10px; position:relative; top:-2px; }}
 header .note{{ margin-left:auto; color:var(--muted); font-size:.82rem; }}
 main{{ max-width:1400px; margin:0 auto; padding:22px 24px; display:grid;
        grid-template-columns:minmax(0,1.05fr) minmax(0,1fr); gap:22px; align-items:start; }}
 .right{{ display:flex; flex-direction:column; gap:22px; }}
 .card{{ background:#fff; border:1px solid var(--border); border-radius:10px;
         box-shadow:0 1px 3px rgba(20,30,40,.06); overflow:hidden; }}
 .card h2{{ margin:0; padding:11px 16px; font-size:.9rem; font-weight:600;
            color:var(--muted); border-bottom:1px solid var(--border); }}
 .card .body{{ padding:14px 16px; }}
 .card img{{ display:block; max-width:100%; height:auto; margin:0 auto; }}
 table{{ border-collapse:collapse; width:100%; font-size:12.5px; }}
 th,td{{ border:1px solid var(--border); padding:5px 8px; text-align:left; }}
 th{{ background:var(--bg); }}
 .waiting{{ color:var(--muted); font-style:italic; text-align:center; padding:26px 12px; }}
 @media (max-width:900px){{ main{{ grid-template-columns:1fr; }} }}
</style></head><body>
<header>
 <h1>Catalysis AutoResearch</h1><span class="live">LIVE</span>
 <span class="note">auto-refreshing every 5s</span>
</header>
<main>
 <section class="card"><h2>Current model fit</h2><div class="body">{fit}</div></section>
 <div class="right">
  <section class="card"><h2>AutoResearch progress</h2><div class="body">{progress}</div></section>
  <section class="card"><h2>Experiment ledger</h2><div class="body">{table}</div></section>
 </div>
</main>
</body></html>"""


def _img(name):
    f = DASH / name
    if f.exists():
        return f'<img src="/{name}?t={f.stat().st_mtime}">'
    return '<div class="waiting">waiting for the first run…</div>'


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


class _Server(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    DASH.mkdir(exist_ok=True)
    try:
        httpd = _Server(("127.0.0.1", args.port), Handler)
    except OSError as e:
        raise SystemExit(f"port {args.port} is busy ({e}); try: uv run dashboard.py --port 8001")
    with httpd:
        print(f"dashboard: http://localhost:{args.port}  (Ctrl-C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
