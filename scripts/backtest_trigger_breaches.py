from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 

from energy_risk.backtest import realised_window_stats
from energy_risk.data import load_brent
from energy_risk.pricing import price_policy
from energy_risk.returns import log_returns
from energy_risk.simulate import sim_block_bootstrap, simulate_gbm

HORIZON = 63
TRIGGER_FRACTIONS = (1.00, 1.05, 1.1, 1.2, 1.3, 1.5)
SPLIT_DATE = "2010-01-01"
N_PATHS = 100_000
BLOCK_DAYS = 21
SEED = 42

prices = load_brent("data/raw/brent_fred.csv")
r = log_returns(prices)

def model_predictions(fit_returns):
    # Prices sim from s0 = 1, so a trigger of k means k * s0 (starting price)
    r0 = fit_returns - fit_returns.mean()
    sigma = r0.std() * 252**(0.5)
    simulated = {
        "GBM" : simulate_gbm(1.0, 0.5 * sigma**2, sigma, HORIZON, N_PATHS, seed=SEED),
        "Block Bootstrap": sim_block_bootstrap(1.0, r0, HORIZON, N_PATHS, block=BLOCK_DAYS, seed=SEED),
    }
    out = {}
    for name, paths in simulated.items():
        results = [price_policy(paths, k) for k in TRIGGER_FRACTIONS]
        out[name] = pd.DataFrame({
            "prob_breach": [x["prob_trigger"] for x in results],
            "expected_payout_pct" : [x["expected_payout"] * 100 for x in results], 
        })
    return sigma, out

def compare(setting, fit_returns, start):
    sigma, preds = model_predictions(fit_returns)
    real = realised_window_stats(prices, HORIZON, TRIGGER_FRACTIONS, start=start)
    n_eff = max(real["n_windows"].iloc[0] / HORIZON, 1)
    p = real["prob_breach"]
    table = pd.DataFrame({
        "setting": setting,
        "trigger_pct": real["trigger_pct"],
        "realised_prob": p,
        "realised_se": np.sqrt(p * (1 - p) / n_eff),
        "gbm_prob": preds["GBM"]["prob_breach"],
        "block_prob": preds["Block Bootstrap"]["prob_breach"],
        "realised_payout_pct": real["expected_payout_pct"],
        "gbm_payout_pct": preds["GBM"]["expected_payout_pct"],
        "block_payout_pct": preds["Block Bootstrap"]["expected_payout_pct"],
        "n_windows": real["n_windows"],
    })
    print(f"\n=== {setting} ===")
    print(f"Models Fitted with Annualised Volatilty {sigma:.1%}; "
          f"{real['n_windows'].iloc[0]} windows (about {n_eff:.0f} independent)")
    show = table.drop(columns=["setting", "n_windows"]).copy()
    for col in ["realised_prob", "realised_se", "gbm_prob", "block_prob"]:
        show[col] = (show[col] * 100).round(1)
    print("Probabilities in %, Payouts as % of the Starting Price")
    print(show.round(2).to_string(index=False))
    return table

in_sample = compare("In-Sample (Models Fitted on All Data, Tested on All Windows)", r, None)
out_sample = compare(f"Out of Sample (Models Fitted Before {SPLIT_DATE}, Tested from {SPLIT_DATE})", r[r.index < SPLIT_DATE], SPLIT_DATE)

Path("results").mkdir(exist_ok=True)
pd.concat([in_sample, out_sample]).round(5).to_csv("results/backtest_trigger_breaches.csv", index=False)

plt.close()
Path("figures").mkdir(exist_ok=True)
fig, ax = plt.subplots(1,2, figsize=(12,5), sharey=True)
for a, table, title in (
    (ax[0], in_sample, "In-Sample: Models Fitted on All Data"),
    (ax[1], out_sample, f"Out-of Sample: Fitted Before {SPLIT_DATE[:4]}, Tested From {SPLIT_DATE}")
):
    for col, label in (("realised_prob", "Realised (history)"), ("gbm_prob", "GBM"), ("block_prob", "Block Bootstrap")):
        a.plot(table["trigger_pct"], (table[col] * 100).replace(0, np.nan), marker="o", label=label)
    a.set_title(title)
    a.set_xlabel("Trigger (% of Starting Price)")
    a.set_yscale("log")
    a.grid(alpha=0.3)
    a.legend()
ax[0].set_ylabel(f"Probability Average Price Over {HORIZON} Days Exceed Trigger (%, log scale)")
plt.tight_layout()
plt.savefig("figures/brent_backtest_breach_prob.png", dpi=150)
#plt.show()
