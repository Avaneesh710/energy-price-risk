import numpy as np 
import pandas as pd 

def realised_window_stats(prices, horizon, trigger_fractions, start=None, exclude=None):
    # For every historical start date t, compare avg of next 'horizon' prices with trigger set at k * price at t
    p = prices.values.astype(float)
    n = len(p) - horizon
    if n <= 0:
        raise ValueError("Price Series is Shorter than the Horizon")
    csum = np.concatenate([[0], np.cumsum(p)])
    avg_next = (csum[horizon + 1:] - csum[1:n+1]) / horizon
    ratio = avg_next / p[:n]
    starts = prices.index[:n]
    keep = np.ones(n, dtype=bool)
    if start is not None:
        keep &= starts >= pd.Timestamp(start)
    if exclude is not None:
        lo, hi = pd.Timestamp(exclude[0]), pd.Timestamp(exclude[1])
        keep &= ~((starts >= lo) & (starts <= hi))
    ratio = ratio[keep]
    if len(ratio) == 0:
        raise ValueError("No Windows Start On or After the Given Start Date")
    rows = []
    for k in trigger_fractions:
        rows.append({
            "trigger_pct" : 100 * k,
            "prob_breach" : (ratio > k).mean(),
            "expected_payout_pct" : np.maximum(ratio - k, 0.0).mean() * 100,
            "n_windows": len(ratio),
        })
    return pd.DataFrame(rows)