import json
import threading
import urllib.request

import server


def test_ledger_payload_derives_iter_and_nulls_non_finite(tmp_path):
    tsv = tmp_path / "results.tsv"
    tsv.write_text(
        "commit\telbo\tmass_residual\tmass_gate\tstatus\tdescription\n"
        "aaa1111\t44.16\t2.4e-07\tPASS\tkeep\tbaseline\n"
        "bbb2222\tnan\t\t\tcrash\ttimeout after 5 min\n"
    )
    out = server.ledger_payload(tsv)
    json.dumps(out, allow_nan=False)  # strictly valid JSON
    r0, r1 = out["rows"]
    assert r0["iter"] == 0 and r0["elbo"] == 44.16 and r0["mass_gate"] == "PASS"
    assert r1["iter"] == 1 and r1["elbo"] is None and r1["status"] == "crash"
    assert r1["mass_gate"] is None and r1["mass_residual"] is None


def test_ledger_payload_ungated_header_lacks_mass_columns(tmp_path):
    tsv = tmp_path / "results.tsv"
    tsv.write_text("commit\telbo\tstatus\tdescription\naaa\t44.0\tkeep\tbaseline\n")
    row = server.ledger_payload(tsv)["rows"][0]
    assert row["mass_gate"] is None and row["mass_residual"] is None


def test_ledger_payload_missing_or_header_only(tmp_path):
    assert server.ledger_payload(tmp_path / "nope.tsv") == {"rows": []}
    tsv = tmp_path / "results.tsv"
    tsv.write_text("commit\telbo\tmass_residual\tmass_gate\tstatus\tdescription\n")
    assert server.ledger_payload(tsv) == {"rows": []}


def test_state_payload(tmp_path):
    assert server.state_payload(tmp_path / "state.json") == {"ready": False}
    good = tmp_path / "state.json"
    good.write_text(json.dumps({"elbo": 44.0}))
    assert server.state_payload(good) == {"elbo": 44.0, "ready": True}
    bad = tmp_path / "bad.json"
    bad.write_text("{half written")
    assert server.state_payload(bad) == {"ready": False}


def test_http_endpoints_and_static(tmp_path, monkeypatch):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<h1>ok</h1>")
    monkeypatch.setattr(server, "DIST", dist)
    monkeypatch.setattr(server, "RESULTS", tmp_path / "results.tsv")
    monkeypatch.setattr(server, "STATE", tmp_path / "state.json")
    httpd = server.make_server(0)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/state") as r:
            assert json.load(r) == {"ready": False}
            assert r.headers["Cache-Control"] == "no-store"
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/ledger") as r:
            assert json.load(r) == {"rows": []}
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as r:
            assert b"ok" in r.read()
    finally:
        httpd.shutdown()
