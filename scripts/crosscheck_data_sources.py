import pandas as pd 
from energy_risk.data import load_brent

fred = load_brent("data/raw/brent_fred.csv").rename("fred")
dh = load_brent("data/raw/brent_datahub.csv").rename("datahub")

m = pd.concat([fred,dh], axis=1) # outer join on date index

print("rows (fred, datahub, union):", len(fred), len(dh), len(m))
print("FRED range: ", fred.index.min().date(), "to", fred.index.max().date())
print("Datahub range: ", dh.index.min().date(), "to", dh.index.max().date())

both = m.dropna()
#print(both)
diff = (both["fred"] - both["datahub"]).abs()
print("max abs diff:", diff.max())
print("rows differing by more than 0.005:", (diff > 0.005).sum())

only_one = m[m["fred"].isna() ^ m["datahub"].isna()]  # detects missing values ^ is XOR condition

print("dates present in only one file:", len(only_one))
print(only_one.head(10))
print(only_one.tail(10))

print(m.loc["2020-04-17": "2020-04-24"])
print(m.loc["1991-01-15": "1991-01-18"]) # extreme days