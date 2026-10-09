import numpy as np

def simulate_gbm(s0, mu, sigma, days, n_paths, seed=42):   
    rng = np.random.default_rng(seed)                              # makes run reproducible
    dt =  1 / 252                                                  # one trading day as a fration of a year
    z = rng.standard_normal((n_paths, days))                       # grid of independent standard normal draws, one per simulated path 
    steps = (mu - 0.5 * sigma**2 ) * dt + sigma * np.sqrt(dt) * z  # formula applied to every cell giving each days log return
    return s0 * np.exp(np.cumsum(steps, axis=1))                   # cumsum adds along each row gives ln(S_t / S_0) each day. exp coverts back to price ratios, * s0 gives price paths.
    
    # uses geometric Brownian Motion (gbm): price follows dS = μ*S*dt + σ*S*dW 
    # with Ito's lemma dln(S) = (μ - 0.5σ^2)*dt + σdW. 
    # Over one step length of dt the log return is normal with mean of (μ - 0.5σ^2)*dt and variance of σ^2*dt 
    # the -0.5σ^2 term appears as the avg of exp(x) is greater than exp(avg_x) (Jensen's inequality), cancels exactly when it takes expected price which grows at rate μ 
    # mu hard to estimate as mean of daily returns noisy so assume mu = 0

def simulate_bootstrap(s0, returns, days, n_paths, seed = 42):
    rng = np.random.default_rng(seed)
    draws = rng.choice(returns.values, size=(n_paths, days))
    return s0 * np.exp(np.cumsum(draws, axis=1))
    # draws returns at random with replacement from actual history, keeps real tails but treats days as indep so loses volatility clustering .
    # Comparing shows how  much normal distrib matters.