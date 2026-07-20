import pathlib
import numpy as np
import prepare


def test_save_fit_plot_writes_png(tmp_path):
    species = ["NO3", "NO2", "N2", "NH3", "N2O", "X"]
    G = 361
    traj = np.linspace(1.0, 0.0, G)[:, None] * np.ones((1, len(species))) / len(species)
    metrics = {"elbo": 50.0, "mass_gate": True}
    out = tmp_path / "fit.png"
    prepare.save_fit_plot(species, traj, 0.5, metrics, out)
    assert out.exists() and out.stat().st_size > 1000


def test_save_progress_plot_writes_png(tmp_path):
    tsv = tmp_path / "results.tsv"
    tsv.write_text(
        "commit\telbo\tmass_residual\tmass_gate\tstatus\tdescription\n"
        "aaa\t44.0\t1e-7\tPASS\tkeep\tbaseline\n"
        "bbb\t60.0\t1e-7\tPASS\tkeep\thidden X\n"
        "ccc\t55.0\t1e-7\tPASS\tdiscard\todds<1\n"
    )
    out = tmp_path / "progress.png"
    prepare.save_progress_plot(tsv, out)
    assert out.exists() and out.stat().st_size > 1000


def test_results_table_html_lists_rows(tmp_path):
    tsv = tmp_path / "results.tsv"
    tsv.write_text(
        "commit\telbo\tmass_residual\tmass_gate\tstatus\tdescription\n"
        "aaa\t44.0\t1e-7\tPASS\tkeep\tbaseline\n"
    )
    html = prepare.results_table_html(tsv)
    assert "<table" in html and "baseline" in html and "44.0" in html


def test_results_table_html_empty(tmp_path):
    tsv = tmp_path / "results.tsv"
    tsv.write_text("commit\telbo\tmass_residual\tmass_gate\tstatus\tdescription\n")
    assert "No runs" in prepare.results_table_html(tsv)
