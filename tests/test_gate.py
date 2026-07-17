import numpy as np
import prepare


def test_conserving_mass_passes():
    total = np.full(7, prepare.TOTAL0)  # exactly 500 at every measured time
    assert prepare.mass_gate(total) is True
    assert prepare.mass_residual(total) == 0.0


def test_leaking_mass_fails():
    # 5% of the mass has leaked away at one time — above the 2% tolerance.
    total = np.full(7, prepare.TOTAL0)
    total[3] = prepare.TOTAL0 * 0.95
    assert prepare.mass_residual(total) > prepare.MASS_TOL
    assert prepare.mass_gate(total) is False


def test_odds_rule_accepts_only_higher_evidence():
    assert prepare.accept(45.0, 44.0) is True   # higher ELBO -> keep
    assert prepare.accept(44.0, 44.0) is False  # ties reject
    assert prepare.accept(43.0, 44.0) is False  # lower ELBO -> reject
