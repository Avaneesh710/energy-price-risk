import numpy as np
import pandas as pd 
import pytest
from scipy.stats import norm
from energy_risk.simulate import simulate_bootstrap, simulate_gbm

def test_gbm_output_shape():
    paths = simulate_gbm(100,0.0, 0.3, days=20, n_paths=50)
    assert paths.shape == (50, 20)                              # tests if the shape of the paths from sim is a certain size

def test_gbm_same_seed_gives_same_paths():
    a = simulate_gbm(100, 0.0, 0.3, 10, 100, seed=7)
    b = simulate_gbm(100, 0.0, 0.3, 10, 100, seed=7)
    assert np.array_equal(a, b)
    
def test_gbm_diff_seeds_give_diff_paths():
    a = simulate_gbm(100, 0.0, 0.3, 10, 100, seed=1)
    b = simulate_gbm(100, 0.0, 0.3, 10, 100, seed=2)
    assert not np.array_equal(a,b)                   # tests if arrays are not equal with diff seeds

def test_gbm_zero_vol_is_deterministic_drift():
    mu, days = 0.05, 30
    paths = simulate_gbm(100,mu, 0.0, days, n_paths=5)
    expected = 100 * np.exp(mu * np.arange(1, days + 1) / 252) 
    assert np.allclose(paths, expected)                         # tests if path calc (zero volatility) is close to the expected vlaue
    
def test_gbm_with_zero_drift_keeps_mean_price_constant():
    paths = simulate_gbm(100, 0.0, 0.4, days=252, n_paths=200_000)
    terminal = paths[:, -1]               # selects final column / last element from last dimension of each row in array
    standard_error = terminal.std() / np.sqrt(len(terminal))
    assert abs(terminal.mean() -100) < 4 * standard_error         
    
def test_gbm_call_price_matches_black_scholes():
    s0, strike, sigma, days = 100.0, 105.0, 0.4, 126
    paths = simulate_gbm(s0, 0.0, sigma, days, n_paths=400_000)    
    payoff = np.maximum(paths[:, -1] - strike, 0.0)
    t = days / 252
    d1 = (np.log(s0 / strike) + 0.5 * sigma**2 * t) / (sigma * np.sqrt(t))
    d2 = d1 - sigma * np.sqrt(t)                                               # Black_Scholes model - reps the theoretical fair value of the option
    exact = s0 * norm.cdf(d1) - strike * norm.cdf(d2)   # First part, s0 * norm.cdf(d1)- expected benefit from purchasing underlying asset, weighted by prob of option finishing in money adjusted for volatility
    standard_error = payoff.std() / np.sqrt(len(payoff)) # Second part, strike * norm.cdf(d2) - present value of exercise price, weighted by risk-neutral prob that option will be exercised
    assert abs(payoff.mean() - exact) < 4 * standard_error
    
def test_bootstrap_output_shape_and_reproducibility():
    r = pd.Series(np.random.default_rng(0).normal(0, 0.02, 500))
    a = simulate_bootstrap(100, r, 15, 40, seed=3)
    b = simulate_bootstrap(100, r, 15, 40, seed=3)
    assert a.shape == (40, 15)
    assert np.array_equal(a, b)


def test_bootstrap_constant_returns_give_exact_growth():
    r = pd.Series([0.01] * 10)
    paths = simulate_bootstrap(100, r, days=5, n_paths=3)
    expected = 100 * np.exp(0.01 * np.arange(1, 6))
    assert np.allclose(paths, expected)
    
# Simulation correctness: with zero volatility, GBM must reproduce the exact drift path. With zero drift, the mean terminal price must stay at the start price. 
# The strongest test compares the Monte Carlo call price with the closed-form Black-Scholes price, which validates the simulator against a known answer