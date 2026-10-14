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
python scripts/step1_crosscheck.py   # data cross-check
python scripts/step2_explore.py      # returns analysis, extreme days, volatility windows, plots
```

## Project structure

```bash
src/energy_risk/ data.py, returns.py, simulate.py, pricing.py
scripts/                                                        # runnable analysis scripts
tests/                                                          # pytest suite
data/raw/                                                       # source CSVs
notebooks/
figures/                                                        # plots
```

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
