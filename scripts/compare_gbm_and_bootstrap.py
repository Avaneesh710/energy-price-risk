from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kurtosis
from energy_risk.data import load_brent
from energy_risk.pricing import price_policy
from energy_risk.returns import log_returns
from energy_risk.simulate import simulate_bootstrap, simulate_gbm, sim_block_bootstrap

HORIZON_DAYS = 63
N_PATHS = 200_000         # 3 months of trading days
SEED = 42

prices = load_brent("data/raw/brent_fred.csv")
r = log_returns(prices)

# --------------- zero-mean log returns, so models differ only in shape of distrib -------------------------

r0 = r - r.mean()
sigma = r0.std() * np.sqrt(252)      # same annualised vol for both models
s0 = prices.iloc[-1]                 # last price
mu = 0.5 * sigma**2                  # makes GBM daily log return have zero mean 

gbm_paths = simulate_gbm(s0, mu, sigma, HORIZON_DAYS, N_PATHS, seed=SEED)
boot_paths = simulate_bootstrap(s0, r0, HORIZON_DAYS, N_PATHS, seed=SEED)

BLOCK_DAYS = 21
block_paths = sim_block_bootstrap(s0, r0, HORIZON_DAYS, N_PATHS, block = BLOCK_DAYS, seed=SEED)
block_term = np.log(block_paths[:, -1] / s0) * 100
# ------------------ Terminal log return over the horizon, in percent ---------------------------------------

gbm_term = np.log(gbm_paths[:, -1] / s0) * 100
boot_term = np.log(boot_paths[:, -1] / s0) * 100
hist_term = r0.rolling(HORIZON_DAYS).sum().dropna().values * 100  # overlapping real windows

samples = {"Historical": hist_term, "GBM" : gbm_term, "Bootstrap" : boot_term, f"Block boot ({BLOCK_DAYS} day block)" : block_term}

print(f"s0 = {s0:.2f} USD/bbl | sigma = {sigma:.1%} | horizon = {HORIZON_DAYS} days")
print(f"historical windows: {len(hist_term)} (overlapping, roughly {len(hist_term) // HORIZON_DAYS} independent)")

quantile_levels = [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
print("\n63-day log return quantiles (%):")
print(f"{'':<12}" + "".join(f"{q:>9.0%}" for q in quantile_levels) + f"{'ex_kurt':>10}") # left /right aligned in a x-char field (row labels)
for name, x in samples.items():
    row = np.quantile(x, quantile_levels)
    print(f"{name:<12}" + "".join(f"{v:>9.1f}" for v in row) + f"{kurtosis(x):>10.2f}")
    
print("\nModel price vs policy price (average-price payout, per barrel):")
print(f"{'trigger':>10} {'model':>12} {'P(payout)':>12} {'E(payout)':>12}")
for k in (1.00, 1.10, 1.20, 1.30):
    for name, paths in (("GBM", gbm_paths), ("Bootstrap", boot_paths), ("block boot", block_paths)):
        res = price_policy(paths, s0 * k)
        print(f"{s0 * k:>10.2f} {name:>12} {res['prob_trigger']:>12.1%} {res['expected_payout'] :>12.2f}")
        
plt.close()        
fig, ax = plt.subplots(2, 1, figsize = (9, 9))
for name, x in samples.items():
    for a, log in ((ax[0], False), (ax[1], True)):
        a.hist(x, bins=120, range=(-80,80), density=True, histtype="step", label=name, log=log)

ax[0].set_title(f"{HORIZON_DAYS}-Trading Day Log Return: Historical vs Simulated")
ax[1].set_title("Same Data, Log y-axis (Shows the tails)")
for a in ax:
    a.set_xlabel(f"{HORIZON_DAYS}-trading day log return (%)")
    a.set_ylabel("Probability density (per percent point)")
    a.grid(alpha=0.3)
    a.legend()
plt.tight_layout()
plt.savefig(f"figures/brent_return_block{BLOCK_DAYS}d.png", dpi=150)
#plt.show()

# Code prints 3 things:
# Sim settings so can check the starting price and starting price and volatiliity
# Table of 63-day return quantiles and excess kutosis for historical data, GBM snd Bootstrap and Block Bootstrap
# Table of breach probability and expected payout per barrel at triggers from 100% to 130% of current price, under each model.

print("\nBlock-length sensitivity (63-day log return quantiles, %):")
print(f"{'block (days)':<14}" + "".join(f"{q:>9.0%}" for q in quantile_levels) + f"{'ex.kurt':>10}")
for b in (5, 10, 21, 42, 63):
    paths = sim_block_bootstrap(s0, r0, HORIZON_DAYS, N_PATHS, block=b, seed = SEED)
    x = np.log(paths[:, -1] / s0) * 100
    row = np.quantile(x, quantile_levels)
    print(f"{b:<14}" + "".join(f"{v:>9.1f}" for v in row) + f"{kurtosis(x):>10.2f}")