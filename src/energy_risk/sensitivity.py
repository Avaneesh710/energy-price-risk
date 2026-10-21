import pandas as pd 
from energy_risk.pricing import price_policy

def sweep_policy_prices(paths, s0, trigger_fractions, terms, loading=0.2, model="model"):
    # paths: simulated prices, one row per path, one column per day.
    # For each term, only the first 'term' days of every path is used
    rows = []
    for term in terms:
        window = paths[:, :term]                           # parses all rows and up to 'term'th column
        for k in trigger_fractions:
            res = price_policy(window, s0 * k, loading)
            rows.append({
                "model": model,
                "term_days" : term,
                "trigger_pct" : 100 * k,
                "trigger_usd": s0 * k,
                "prob_breach" : res["prob_trigger"],
                "expected_payout": res["expected_payout"],
                "std_error" : res["std_error"],
                "premium": res["premium"],
            })
    return pd.DataFrame(rows)