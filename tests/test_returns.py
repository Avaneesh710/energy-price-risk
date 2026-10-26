import numpy as np 
import pandas as pd 
import pytest
from energy_risk.returns import annual_vol, historical_var, log_returns

@pytest.fixture                                                    # decorator for pytest to mark func as test fixture
def prices():
    idx = pd.date_range("2020-01-01", periods=3, freq="D")         # returns pd series indexed by 3-day Datetime index  freq = daily 
    return pd.Series([100.0, 110.0, 99.0], index=idx)

def test_log_returns_match_hand_calc(prices):
    r = log_returns(prices)
    assert r.iloc[0] == pytest.approx(np.log(1.10))
    assert r.iloc[1] == pytest.approx(np.log(0.90))

def test_log_returns_has_one_fewer_val_than_prices(prices):
    assert len(log_returns(prices)) == len(prices) -1
    
def test_log_returns_add_up_over_time(prices):
    total = log_returns(prices).sum()
    assert total == pytest.approx(np.log(prices.iloc[-1] / prices.iloc[0]))
    
def test_annual_vol_uses_sqrt_252_scaling():
    rng = np.random.default_rng(0)                        # rng generator with 0 seed
    r = pd.Series(rng.normal(0,0.02,200))                 # 200 synthetic runs with normal distrib with mean = 0 and std = 0.02
    vol = annual_vol(r, window=len(r)).iloc[-1]           # annual vol func over full obs window and takes only the last value
    assert vol == pytest.approx(r.std() * np.sqrt(252))   
    

def test_annual_vol_first_window_minus_one_values_are_nan():
    r = pd.Series(np.linspace(-0.01, 0.01, 50))
    vol = annual_vol(r, window=30)
    assert vol.iloc[:29].isna().all()                       # first 29 values must be NaN and the rest is not Nan
    assert vol.iloc[29:].notna().all()

def test_historical_var_known_quantile():
    r = np.array([-0.05, -0.02, 0.01, 0.02, 0.03])
    assert historical_var(r, level=0.95) == pytest.approx(0.044)

def test_historical_var_is_positive_for_a_loss_tail():
    rng = np.random.default_rng(1)
    r = rng.normal(0,0.02, 5000)
    assert historical_var(r, 0.95) > 0
    assert historical_var(r, 0.99) > historical_var(r, 0.95)