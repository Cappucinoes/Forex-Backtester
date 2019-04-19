import pandas as pd
from datetime import datetime

df = pd.read_excel(r"C:\Users\Cappucinoe`s Beast\Desktop\Python-Algo\Backtesting\15M_neopt_TP3_SL10_SPREAD\vysledky_stats.xlsx")
df["Date_col"] = df.Date_open.apply(lambda x: x.date())
df["Day_name"] = df.Date_col.apply(lambda x: x.strftime('%A'))
df["hour"] = df.Date_open.apply(lambda x: x.hour)
print(df[["Date_col", "Day_name"]].drop_duplicates().sort_values(by="Date_col"))
print(df.groupby(["Day_name", "balance_effect"]).count().Result)