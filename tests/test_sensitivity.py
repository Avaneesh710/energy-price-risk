import numpy as np
import pytest

from energy_risk.sensitivity  import sweep_policy_prices
from energy_risk.simulate import simulate_gbm

def test_sweep_returns_one_row_per_term_and_trigger():
    paths = simulate_gbm(100,0.0, 0.4, 60, 2_000)
    table = sweep_policy_prices(paths, 100.0, [1.0, 1.1, 1.2], [20, 60], model = "GBM")
    assert len(table) == 6
    assert set(table["model"]) == {"GBM"}
    assert list(table.columns) == [
        "model", "term_days", "trigger_pct", "trigger_usd", "prob_breach", "expected_payout", "std_error", "premium",
    ]


def test_sweep_payout_falls_as_trigger_rises():
    paths = simulate_gbm(100, 0.0, 0.4, 60, 2_000)    
    table = sweep_policy_prices(paths, 100.0, [1.0, 1.1, 1.2, 1.5], [60])
    ordered = table.sort_values("trigger_pct")["expected_payout"]
    assert ordered.is_monotonic_decreasing
    
def test_sweep_uses_only_the_first_term_days():
    paths = np.hstack([np.full((10, 5), 100.0), np.full((10,5), 200.0)])
    table = sweep_policy_prices(paths, 100.0, [1.0], [5, 10])
    short = table[table["term_days"] == 5 ].iloc[0]
    long = table[table["term_days"] == 10 ].iloc[0]
    assert short["expected_payout"] == pytest.approx(0.0)
    assert long["expected_payout"] == pytest.approx(50.0)