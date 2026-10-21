import numpy as np
import pytest

from energy_risk.pricing import price_policy, trigger_payout
from energy_risk.simulate import simulate_gbm


def test_payout_is_excess_over_trigger_when_price_is_constant():
    paths = np.full((4, 10), 120.0)
    assert np.allclose(trigger_payout(paths, trigger=100.0), 20.0)


def test_payout_is_zero_when_price_stays_below_trigger():
    paths = np.full((4, 10), 80.0)
    assert np.allclose(trigger_payout(paths, trigger=100.0), 0.0)


def test_payout_uses_average_price_over_the_term():
    paths = np.array([[90.0, 110.0, 130.0]])
    assert trigger_payout(paths, trigger=100.0)[0] == pytest.approx(10.0)


def test_payout_scales_with_notional():
    paths = np.full((3, 5), 110.0)
    base = trigger_payout(paths, 100.0, notional=1.0)
    scaled = trigger_payout(paths, 100.0, notional=250.0)
    assert np.allclose(scaled, 250.0 * base)


def test_payouts_are_never_negative():
    paths = simulate_gbm(100, 0.0, 0.5, days=60, n_paths=2000)
    assert (trigger_payout(paths, trigger=100.0) >= 0).all()


def test_zero_volatility_policy_price_is_exact():
    paths = simulate_gbm(100, 0.0, 0.0, days=20, n_paths=10)
    result = price_policy(paths, trigger=90.0, loading=0.2)
    assert result["expected_payout"] == pytest.approx(10.0)
    assert result["premium"] == pytest.approx(12.0)
    assert result["prob_trigger"] == pytest.approx(1.0)


def test_higher_trigger_never_raises_the_premium():
    paths = simulate_gbm(100, 0.0, 0.4, days=60, n_paths=20_000)
    premiums = [price_policy(paths, trigger=k)["premium"] for k in (80, 90, 100, 110, 120)]
    assert all(a >= b for a, b in zip(premiums, premiums[1:]))


def test_probability_of_trigger_falls_as_trigger_rises():
    paths = simulate_gbm(100, 0.0, 0.4, days=60, n_paths=20_000)
    probs = [price_policy(paths, trigger=k)["prob_trigger"] for k in (80, 100, 120)]
    assert probs[0] >= probs[1] >= probs[2]
    assert all(0.0 <= p <= 1.0 for p in probs)


def test_premium_is_expected_payout_plus_loading():
    paths = simulate_gbm(100, 0.0, 0.4, days=60, n_paths=5000)
    result = price_policy(paths, trigger=100.0, loading=0.35)
    assert result["premium"] == pytest.approx(result["expected_payout"] * 1.35)


def test_higher_volatility_raises_the_premium():
    low = simulate_gbm(100, 0.0, 0.2, days=60, n_paths=50_000)
    high = simulate_gbm(100, 0.0, 0.6, days=60, n_paths=50_000)
    assert price_policy(high, 100.0)["premium"] > price_policy(low, 100.0)["premium"]


def test_averaging_price_lowers_expected_payout_versus_terminal_price():
    paths = simulate_gbm(100, 0.0, 0.4, days=126, n_paths=100_000)
    average_based = trigger_payout(paths, 100.0).mean()
    terminal_based = np.maximum(paths[:, -1] - 100.0, 0.0).mean()
    assert average_based < terminal_based
    
# Pricing logic: a higher trigger never raises the premium, higher volatility does, and the premium equals expected payout * (1 + loading).
# The last test confirms that averaging the price over the term gives a lower expected payout than using the final price, as averaging smooths out the extremes.

def test_std_error_is_zero_when_every_payout_is_identical():
    paths = np.full((50, 5), 120.0)
    assert price_policy(paths, trigger=100.0)["std_error"] == pytest.approx(0.0)
    
def test_std_error_matches_formula_and_shrinks_with_more_paths():
    small = simulate_gbm(100,0.0, 0.4, 30, 2_000)
    large = simulate_gbm(100,0.0, 0.4, 30, 32_000, seed =1)
    payouts = trigger_payout(small, 100.0)
    expected = payouts.std(ddof=1) / np.sqrt(len(payouts))
    assert price_policy(small, 100.0)["std_error"] == pytest.approx(expected)
    assert price_policy(large, 100.0)["std_error"] < price_policy(small, 100.0)["std_error"]