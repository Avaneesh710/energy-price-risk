# Energy Price Risk: Brent Crude Trigger-Payout Pricing

A Python project that studies Brent crude price behaviour and prices a simple
"pay the excess above a trigger" policy by Monte Carlo simulation.
This is an educational project and not a production pricing model.

**Status:** data loaded and validated; returns analysis, extreme-day check and
volatility sensitivity complete; tests, simulation and pricing in progress.

## Question

How likely is a given energy price trigger to be breached, and what is the
expected payout of a policy that pays the excess above it?

## Data

- Series: Europe Brent Spot Price FOB, daily, USD per barrel (FRED: DCOILBRENTEU, from the US EIA).
- Primary file: `data/raw/brent_fred.csv`. Backup: `data/raw/brent_datahub.csv` (DataHub copy of the EIA data).
- Downloaded: 1 October 2026. Raw files are unmodified; all cleaning happens in code.
- Coverage: 20 May 1987 to 29 September 2026. 9,097 price observations
  (about 231 per year, as holidays are missing).
- Cross-check (`scripts/step1_crosscheck.py`): FRED and DataHub compared by date.
  Both files have 9,097 rows and the same date range. Maximum absolute
  difference is 0.0, with 0 rows differing by more than 0.005 and 0 dates present
  in only one file. Both files share the same upstream source (the EIA), so this
  confirms the download and parsing, not the EIA's own accuracy.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

## Run

```bash
python scripts/crosscheck_data_sources.py             # data cross-check
python scripts/explore_returns_and_volatility.py      # returns analysis, extreme days, volatility windows, plots
python scripts/compare_gbm_and_bootstrap.py           # simulation vs history
python -m pytest -v                                   # run the test suite
```

## Project structure

```bash
src/energy_risk/ data.py, returns.py, simulate.py, pricing.py
scripts/                                                        # runnable analysis scripts
tests/                                                          # pytest suite
data/raw/                                                       # source CSVs
notebooks/
figures/                                                        # saved plots
```

## Testing

`python -m pytest -v` runs 27 tests covering data loading, returns, volatility, VaR,
the GBM and bootstrap simulators and the pricing functions. Checks include hand
calculations, reproducibility with fixed seeds, and a comparison of the Monte Carlo
call price with the Black-Scholes formula (agreement within 4 standard errors).

## Results so far

- Daily log returns: std 2.69%, skew -1.53, excess kurtosis 53.7 (very fat tails).
- Historical 95% daily VaR: 3.79% (downside), 3.70% (upside).
- Days with |log return| above 0.25, confirmed identical in both source files:

| Date       | Price change (USD/bbl) | Simple change | Log return |
| ---------- | ---------------------- | ------------- | ---------- |
| 1991-01-17 | 30.28 to 21.10         | -30.3%        | -0.361     |
| 2020-03-09 | 45.60 to 35.33         | -22.5%        | -0.255     |
| 2020-03-31 | 19.19 to 14.85         | -22.6%        | -0.256     |
| 2020-04-02 | 14.97 to 20.24         | +35.2%        | +0.302     |
| 2020-04-21 | 17.36 to 9.12          | -47.5%        | -0.644     |
| 2020-04-22 | 9.12 to 13.77          | +51.0%        | +0.412     |

Each sits inside a coherent run of prices, so all are kept in the data.

## Simulation comparison

Three-month (63 trading day) horizon from the latest price (113.96 USD/bbl).
Real returns are demeaned, GBM uses the same volatility (42.8%) and a drift that
makes its log returns zero-mean, so the models differ only in distribution shape.
Historical windows are overlapping (about 143 independent).

| 63-day log return (%) | 1%    | 5%    | 25%   | 50%  | 75%  | 95%  | 99%  | Excess kurtosis |
| --------------------- | ----- | ----- | ----- | ---- | ---- | ---- | ---- | --------------- |
| Historical            | -67.4 | -32.5 | -10.4 | 0.3  | 11.6 | 30.8 | 57.0 | 6.40            |
| GBM                   | -49.8 | -35.2 | -14.3 | -0.0 | 14.4 | 35.3 | 49.7 | 0.02            |
| Bootstrap             | -54.9 | -34.9 | -13.5 | 0.3  | 13.9 | 34.1 | 49.8 | 0.83            |

Findings: the bootstrap's kurtosis matches the iid expectation (daily 53.7 / 63),
while real 63-day returns are much fatter-tailed (6.40), which points to volatility
clustering. Real returns are more peaked in the middle and heavier in the extreme
tails than both models. A single volatility overstates ordinary-period spread and
understates crisis moves.

Expected payout per barrel of an average-price policy (before any loading):

| Trigger (USD) | GBM  | Bootstrap |
| ------------- | ---- | --------- |
| 113.96 (100%) | 6.40 | 6.18      |
| 125.36 (110%) | 2.30 | 2.14      |
| 136.75 (120%) | 0.67 | 0.64      |
| 148.15 (130%) | 0.16 | 0.19      |

Model differences are small up to a 120% trigger and larger far out in the tail.

### Volatility by window

Annualised using sqrt(252) scaling.

| Window                              | Annualised volatility | Observations |
| ----------------------------------- | --------------------- | ------------ |
| Full history                        | 42.8%                 | 9,096        |
| Full history excluding Mar-May 2020 | 38.8%                 | 9,035        |
| Last 5 years (from 1 Oct 2021)      | 42.2%                 | 1,262        |
| Last 1 year (from 1 Oct 2025)       | 60.9%                 | 252          |

Mar-May 2020 is under 1% of the days but adds about 4 percentage points to
full-history volatility. The last year is a markedly higher-volatility regime,
so pricing results will be shown for low, base and high volatility cases.

### Block bootstrap

Resampling runs of consecutive days keeps volatility clustering. Longer blocks
move the simulated distribution toward history:

| Block length | 1%    | 5%    | 25%   | 75%  | 95%  | 99%  | Excess kurtosis |
| ------------ | ----- | ----- | ----- | ---- | ---- | ---- | --------------- |
| 10 days      | -54.2 | -34.1 | -12.6 | 13.0 | 32.6 | 50.1 | 1.74            |
| 21 days      | -56.2 | -33.3 | -12.3 | 12.8 | 32.5 | 53.1 | 3.35            |
| 63 days      | -67.0 | -32.4 | -10.4 | 11.6 | 30.8 | 57.1 | 6.32            |

A 63-day block equals the horizon, so each path is one real historical window and
the output replays history by construction. It is a reference, not a fitted model.

Expected payout per barrel (breach probability), average-price policy, before loading:

| Trigger (USD) | GBM          | Bootstrap    | Block 10d    | Block 21d    | Block 63d    |
| ------------- | ------------ | ------------ | ------------ | ------------ | ------------ |
| 113.96 (100%) | 6.40 (50.9%) | 6.18 (51.3%) | 5.88 (51.4%) | 5.91 (51.7%) | 5.70 (51.9%) |
| 125.36 (110%) | 2.30 (22.9%) | 2.14 (21.7%) | 1.97 (19.9%) | 2.02 (19.4%) | 1.96 (17.6%) |
| 136.75 (120%) | 0.67 (7.8%)  | 0.64 (6.9%)  | 0.65 (5.9%)  | 0.74 (5.7%)  | 0.84 (5.0%)  |
| 148.15 (130%) | 0.16 (2.1%)  | 0.19 (1.9%)  | 0.27 (1.8%)  | 0.36 (1.9%)  | 0.50 (1.8%)  |

At the money the models agree within about 4–11%. Far out of the money the
expected payout varies two- to threefold, because fat tails make breaches rare
but large. Results are reported as a model range, with the 21-day block
bootstrap as the central case.

![63-day return distributions](figures/brent_return_distributions_block21d.png)

### Context for the extreme days

- **21 April 2020.** The day before, US WTI futures traded below zero for the
  first time, as demand collapsed and US crude storage filled. On 21 April Brent
  fell to 9.12 USD per barrel, its lowest daily price in decades
  ([EIA](https://www.eia.gov/todayinenergy/detail.php?id=46336)). Brent contracts
  can be cash-settled, so the WTI storage squeeze did not apply to them directly
  ([AMRO](https://www.amro-asia.org/wp-content/uploads/2020/04/AMRO-Oil-Market-Update_22-Apr-2020.pdf)).
  The following day's +51% is a partial rebound.
- **17 January 1991.** The first day of Operation Desert Storm. US crude fell by
  about a third in one session, from 32.25 to 21.48 USD
  ([Washington Post](https://www.washingtonpost.com/climate-environment/oil-price-war-threatens-widespread-collateral-damage/2020/03/09/3e42c9e2-6207-11ea-acca-80c22bbee96f_story.html)).
  This Brent series fell 30.3% on the same day.
- **9 March 2020.** Benchmark crude fell more than 20% in a day as an oil price
  war began ([Washington Post](https://www.washingtonpost.com/climate-environment/oil-price-war-threatens-widespread-collateral-damage/2020/03/09/3e42c9e2-6207-11ea-acca-80c22bbee96f_story.html)).
  The causes of the 31 March and 2 April 2020 moves have not been investigated.

## Assumptions and limitations

- Annualisation uses 252 days although the series has about 231 observations a year.
- Both data sources derive from the EIA, so the cross-check is not independent.
- This is a spot price series. Brent futures quoted on 21 April 2020 were
  reported at roughly 17 to 23 USD, well above 9.12, so a futures-based series
  would show a smaller 2020 move.
- GBM and the iid bootstrap assume constant volatility and independent returns,
  and both understate extreme 3-month moves seen in historical data.
- Only about 143 independent 3-month windows exist, so tail estimates rest on a
  few episodes (2008-09 and 2020).
