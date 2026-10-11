
import numpy as np
import matplotlib.pyplot as plt
from energy_risk.data import load_brent
from energy_risk.returns import log_returns, annual_vol, historical_var      # made importable by pyproject.toml file

prices = load_brent("data/raw/brent_fred.csv")
r = log_returns(prices)

print(prices.head(3)); print(prices.tail(3))  # first and last 3 rows of dataframe
print(prices.describe())                      # description of dataframe
print(r.describe())
print("skew:", r.skew(), "| excess kurtosis:", r.kurt() )  
# unbiased skew of dataset measures asymm relative to normal distrib (skew =0) 
# kurtosis is degree of tailedness in a prob distrib kurt val for normal distrib is 3. excess kurtosis subtracts 3 so mean for normal distrib is 0.

print("annual vol, full history:", r.std()*np.sqrt(252))
print("annual vol, last 5 yrs:", r[r.index >= "2021-10-01"].std() * np.sqrt(252))
print("downside VaR95:", historical_var(r), "| upside 95% quantile:", np.quantile(r,0.95))
print("largest daily moves:\n:", r.abs().sort_values().tail(5))

plt.close()
fig, ax = plt.subplots(3,1, figsize=(10,10))

prices.plot(ax=ax[0], title = "Brent Crude Spot Price, 1987 to Present")
ax[0].set_xlabel("Date"); ax[0].set_ylabel("Price(USD per Barrel)")

r.hist(bins=100, ax=ax[1]); ax[1].set_title("Distribution of Daily Log Returns")
ax[1].set_xlabel("Daily Log Return"); ax[1].set_ylabel("Number of Trading Days")

annual_vol(r).plot(ax=ax[2], title="30-day Rolling Annualised Volatility")
ax[2].set_xlabel("Date"); ax[2].set_ylabel("Annualised Volatility (%)")

for a in ax:
    a.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("notebooks/brent_log_returns+volatility.png", dpi=150)

