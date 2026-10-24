import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "crosscheck_data_sources.py",
    "explore_returns_and_volatility.py",
    "compare_gbm_and_bootstrap.py",
    "pricing_sensitivity_analysis.py",
    "backtest_trigger_breaches.py"
]

env = dict(os.environ, MPLBACKEND="Agg")      # Saves figures without opening windows
for name in SCRIPTS:
    print(f"\n=== {name} ===", flush=True)
    subprocess.run([sys.executable, str(Path("scripts") / name)], check=True, env=env, cwd=ROOT)
print("\nAll Scripts Finished")