import numpy as np

def trigger_payout(paths, trigger, notional=1.0):
    avg_price = paths.mean(axis=1)                          # averages each simulated path over policy term, gives one avg price per path
    return notional * np.maximum(avg_price - trigger, 0.0)  # payout max, excess over trigger or 0, same shape as call option

def price_policy(paths, trigger, loading=0.2): 
    payouts = trigger_payout(paths, trigger)
    return {
        "prob_trigger" : (payouts > 0).mean(),        # fracton of paths with payout, proportion of true values
        "expected_payout" : payouts.mean(),           # Monte-Carlo estimate of expected payout, 'fair' premium before margin, ignores discounting and risk-neutral pricing (simplification)
        "premium": payouts.mean() * (1 + loading),    # loading is assumed margin 20% made up number.
        "payout_95pct" : np.quantile(payouts, 0.95),  # size of bad outcome, relates to how much capital a seller would need to hold.
    }
    
    # Monte Carlo estimate has standard error of σ /√N where σ is std. deviation of payouts and N is number of paths.