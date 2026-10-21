from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from energy_risk.data import load_brent
from energy_risk.returns import log_returns
from energy_risk.sensitivity import sweep_policy_prices
from energy_risk.simulate import sim_block_bootstrap, simulate_gbm

TERMS = (21, 63, 126)                      # 1, 3 and 6 months of trading days
TRIGGER_FRACTIONS = (1.00, 1.05, 1.1, 1.2, 1.3, 1.5)
N_PATHS = 100_000                           # Use 50_000 instead of 100,000 due if low laptop memory
LOADING = 0.20                             # This is an assumed margin, not a market figure
BLOCK_DAYS = 21
SEED = 42
MAX_TERM = max(TERMS) 
MAIN_TERM = 63

prices = load_brent("data/raw/brent_fred.csv")
r = log_returns(prices)
r0 = r - r.mean()
s0 = prices.iloc[-1]

# 3 volatility cases for GBM, taken from the data (README volatility table)
crisis = (r.index >= "2020-03-01") & (r.index <= "2020-05-31")
vol_cases = {
    "low" : r[~crisis].std() * np.sqrt(252),
    "base" : r.std() * 252**(0.5),
    "high": r.iloc[-252:].std() * 252**(0.5),     # latest 252 observations (last year)
}

tables = []
for case, sigma in vol_cases.items():
    # drift chosen so daily log return has zero mean, as in model comparison
    paths = simulate_gbm(s0, 0.5 * sigma**2, sigma, MAX_TERM, N_PATHS, seed=SEED)
    label = f"GBM ({case} vol, {sigma:.0%})"
    tables.append(sweep_policy_prices(paths, s0, TRIGGER_FRACTIONS, TERMS, LOADING, model = label))
    del paths

paths = sim_block_bootstrap(s0, r0, days = MAX_TERM, n_paths=N_PATHS, seed = SEED) 
label = f"Block bootstrap ({BLOCK_DAYS}d)"
tables.append(sweep_policy_prices(paths, s0, TRIGGER_FRACTIONS, TERMS, LOADING, model = label))
del paths

results = pd.concat(tables, ignore_index=True)
Path("results").mkdir(exist_ok=True)
results.round(4).to_csv("results/pricing_sensitivity.csv", index=False)

model_order = list(dict.fromkeys(results["model"]))
print(f"current price s0 = {s0:.2f} USD/bbl, {N_PATHS:,} paths per model")
for term in TERMS:
    sub = results[results["term_days"] == term]
    payout = sub.pivot(index="trigger_pct", columns="model", values="expected_payout")[model_order]
    prob = sub.pivot(index="trigger_pct", columns="model", values="prob_breach")[model_order]
    print(f"\nExpected payout, USD per barrel, term = {term} trading days")
    print(payout.round(2).to_string())
    print(f"largest Monte Carlo standard error in this table: {sub['std_error'].max():.3f} USD")
    print(f"Probability the policy pays out (%), term = {term} trading days")
    print((prob * 100).round(1).to_string())
    
Path("figures").mkdir(exist_ok=True)

main = results[results["term_days"] == MAIN_TERM]
plt.close()
fig, ax = plt.subplots(1, 2, figsize=(12,5))
for model, grp in main.groupby("model", sort=False):
    grp = grp.sort_values("trigger_pct")
    ax[0].plot(grp["trigger_pct"], (grp["expected_payout"] / s0 * 100).replace(0, np.nan), marker="o", label=model)
    ax[1].plot(grp["trigger_pct"], (grp["prob_breach"] * 100).replace(0, np.nan), marker="o", label=model)

ax[0].set_title(f"{MAIN_TERM}-Day Policy: Expected Payout vs Trigger")
ax[0].set_ylabel("Expected Payout (% of Current Price, Log Scale)")

ax[1].set_title(f"{MAIN_TERM}-Day Policy: Chance of a Payout vs Trigger")
ax[1].set_ylabel("Probability of a Payout (%, Log Scale)")
for a in ax:
    a.set_xlabel("Trigger (% of current price)")
    a.set_yscale("log")
    a.grid(alpha=0.3)
    a.legend(fontsize=8)
plt.tight_layout()
plt.savefig("figures/brent_policy_price_vs_trigger.png", dpi=150)

at_110 = results[np.isclose(results["trigger_pct"], 110)]
fig, ax = plt.subplots(figsize=(8,5))
for model, grp in at_110.groupby("model", sort=False):
    grp = grp.sort_values("term_days")
    ax.plot(grp["term_days"], grp["expected_payout"] / s0 * 100, marker="o", label=model)

ax.set_title("Expected Payout vs Policy Term (Trigger at 110% of Current Price)")
ax.set_xlabel("Policy Term (Trading Days)")
ax.set_ylabel("Expected Payout (% of Current Price)")
ax.grid(alpha=0.3)
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig("figures/brent_policy_price_vs_term.png", dpi=150)
#plt.show()