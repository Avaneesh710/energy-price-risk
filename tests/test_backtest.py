import pandas as pd
import pytest

from energy_risk.backtest import realised_window_stats


def test_constant_prices_breach_only_for_triggers_below_start():
    prices = pd.Series(100.0, index=pd.date_range("2020-01-01", periods=30))
    table = realised_window_stats(prices, horizon=5, trigger_fractions=[0.9, 1.0, 1.1])
    assert table["prob_breach"].tolist() == [1.0, 0.0, 0.0]
    assert table["expected_payout_pct"].iloc[0] == pytest.approx(10.0)


def test_known_series_matches_hand_calculation():
    prices = pd.Series([100.0, 110.0, 120.0, 130.0, 140.0], index=pd.date_range("2020-01-01", periods=5))             
    table = realised_window_stats(prices, horizon=2, trigger_fractions=[1.14])
    row = table.iloc[0]
    assert row["n_windows"] == 3
    assert row["prob_breach"] == pytest.approx(1 / 3)
    assert row["expected_payout_pct"] == pytest.approx((1.15 - 1.14) / 3 * 100)


def test_start_date_removes_earlier_windows():
    prices = pd.Series(100.0, index=pd.date_range("2020-01-01", periods=30))
    everything = realised_window_stats(prices, 5, [1.0])
    later = realised_window_stats(prices, 5, [1.0], start="2020-01-15")
    assert later["n_windows"].iloc[0] < everything["n_windows"].iloc[0]


def test_series_shorter_than_horizon_raises():
    prices = pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2020-01-01", periods=3))
    with pytest.raises(ValueError):
        realised_window_stats(prices, horizon=5, trigger_fractions=[1.0])