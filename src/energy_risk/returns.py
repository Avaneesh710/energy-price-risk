import numpy as np

def log_returns(prices):
    return np.log(prices / prices.shift(1)).dropna() 
    
    # log returns simpler to add consecutive dates than simple returns:  r_t = ln(P_t / P_{t-1}) = ln(1 + R_t)
    # where R_t = (P_t - P_{t-1}) / P_{t-1} ,  t is current date


def annual_vol(returns, window=30):
    return returns.rolling(window).std() * np.sqrt(252) 
    
    # volatility is standard deviation (std) of returns - how widely they scatter about the mean : std_daily = ((1 / (n-1)) * SUM [i = 1 to n] {(r_i - mean_r)^2 })^(1/2)
    # over 252 trading days annual volatility = sqrt(252) * daily volatility.  AS Variance  = std^2 so annual Variance = 252 * std^2
    # rolling window computes std over sliding window of latest 30 observations so VOL changes through time so first 29 values are NaN as window isnt full.
    # Longer window will be smoother but slower compared to a noiser but fast short window.


def historical_var(returns, level=0.95):
    returns -np.quantile(returns, 1-level)
    
    # VaR is value at risk meaures what loss will be exceded on only 5% of days. It is negative of the (1 - level) quantile of return distribution. - 5% quantile as default.#
    # finds the return below which 95% of observations fail e.g. return = -0.03 so code returns 0.03 so 95% of days the loss is below 3% 
    # uses actual past returns instead of distribution but assumes future looks like sampled past.
    # code measures risk for one who loses when price falls but for fuel buying customers they lose when price rises so need to look at upper tail.