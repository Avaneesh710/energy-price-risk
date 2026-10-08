import pandas as pd

def load_brent(path):
    df = pd.read_csv(path) # loads, reads and parses csv file (this line and below)
    df.columns = ["Date", "Price"]   # for datahub file, for fred file: obsevation_date , DCOILBRENTEU
    df["Date"] = pd.to_datetime(df["Date"])
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")  # blanks turn to Nan (Not a number)
    return df.dropna().set_index("Date").sort_index()["Price"] 
    # ^ removes rows with nan vales then converts date column to a row index (Dataframe) 
    # then orders them from earliest to latest then extracts the price column from these cleaned and indexed rows then returns it as pandas series