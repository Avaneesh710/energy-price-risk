
import numpy as np
import matplotlib.pyplot as plt
from energy_risk.data import load_brent
from energy_risk.returns import log_returns, annual_vol, historical_var      # made importable by pyproject.toml file

#-------------------------------loading data + analysing ----------------------------------
prices = load_brent("data/raw/brent_fred.csv")
r = log_returns(prices)

print(prices.head(3)); print(prices.tail(3))  # first and last 3 rows of dataframe
print(prices.describe())                      # description of dataframe
print(r.describe())
print("skew:", r.skew(), "| excess kurtosis:", r.kurt() )  
# unbiased skew of dataset measures asymm relative to normal distrib (skew =0) 
# kurtosis is degree of tailedness in a prob distrib kurt val for normal distrib is 3. excess kurtosis subtracts 3 so mean for normal distrib is 0.
# kurt = 53.7 and skew = -1.53 so big drops more extreme than big rises - few days dominate everything

print("annual vol, full history:", r.std()*np.sqrt(252))
print("annual vol, last 5 yrs:", r[r.index >= "2021-10-01"].std() * np.sqrt(252))
print("downside VaR95:", historical_var(r), "| upside 95% quantile:", np.quantile(r,0.95))
print("largest daily moves:\n:", r.abs().sort_values().tail(5))

#--------------------------------Plots ----------------------------------------

plt.close()
fig, ax = plt.subplots(3,1, figsize=(10,10))

prices.plot(ax=ax[0], title = "Brent Crude Spot Price, 1987 to Present")
ax[0].set_xlabel("Date"); ax[0].set_ylabel("Price (USD per Barrel)")

(r*100).hist(bins=100, ax=ax[1]); ax[1].set_title("Distribution of Daily Log Returns")
ax[1].set_xlabel("Daily Log Return (%)"); ax[1].set_ylabel("Number of Trading Days")

(annual_vol(r)*100).plot(ax=ax[2], title="30-Day Rolling Annualised Volatility")
ax[2].set_xlabel("Date"); ax[2].set_ylabel("Annualised Volatility (%)")
# 9097 obs so about 231 days per year so over 252 so ann_vol overestimated from 42.8% to around 41%

for a in ax:
    a.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("figures/brent_price_returns_and_volatility.png", dpi=150)

plt.close()
fig2, ax2 = plt.subplots(figsize=(9,4))
(r*100).hist(bins=200, ax=ax2, log=True)
ax2.set_title("Daily Log Returns, Full Range")
ax2.set_xlabel("Daily Log Return (%)"); ax2.set_ylabel("Number of Trading Days (Log Scale)")
plt.tight_layout()
plt.savefig("figures/brent_return_tails_log_scale.png", dpi=150)

# --------------data check on the extreme values -------------------

big = r[r.abs() > 0.25]
print("signed extreme returns:\n", big)
for d in big.index:
    i = prices.index.get_loc(d)
    print(prices.iloc[i-2:i+3].to_string(), "\n")
    
mask = (r.index >= "2020-03-01") & (r.index <= "2020-05-31")

windows = {
    "Full history": r,
    "Last 5 years (from 1 Oct 2021)": r[r.index >= "2021-10-01"],
    "Last 1 year (from 1 Oct 2025)" : r[r.index >= "2025-10-01"],
    "Full history excluding Mar-May 2020": r[~mask],
}

for name, x in windows.items():
    print(f"{name}: {x.std() * np.sqrt(252):.1%} (n={len(x)})")