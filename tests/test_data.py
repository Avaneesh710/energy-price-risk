import pandas as pd
from energy_risk.data import load_brent
import pytest

def test_load_brent_drop_blanks_and_sorts(tmp_path):
    csv = tmp_path / "prices.csv"
    csv.write_text(
        "observation_date, DCOILBRENTEU\n"
        "2020-01-03, 12.0\n"
        "2020-01-01, 10.0\n"
        "2020-01-02, .\n"
        "2020-01-06, \n"
        "2020-01-07, 14.0\n"
    )
    prices = load_brent(csv)
    assert list(prices.values) == [10.0, 12.0, 14.0]
    assert prices.index.is_monotonic_increasing
    assert prices.name == "Price"
    assert isinstance(prices.index, pd.DatetimeIndex)
