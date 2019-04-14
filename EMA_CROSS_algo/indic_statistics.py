import pandas as pd
import datetime

pd.set_option('display.width', 320)
pd.set_option("display.max_columns", 20)

columns = ["Date_open", "Order_type", "Size", "Pair","Open_price", "SL", "TP", "Date_closed", "Closed_price"]
trading_history = pd.read_csv("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/AccountHistory.csv",sep=";", usecols= [i for i in range(14)])

trading_history.loc[trading_history.shape[0]] = trading_history.columns


profit_col = trading_history[trading_history.columns[12]]
trading_history = trading_history[[i for i in trading_history.columns[1:10]]]

trading_history.columns = columns
trading_history["Result"] = profit_col

#print(trading_history.head())
trading_history.Result.loc[244] = float(trading_history.Result.loc[244])
#print(trading_history.Result.apply(lambda x: abs(x)).mean())
trading_history["Result_string"]= trading_history.Result.apply(lambda x: "LOOSE" if x < 0 else "WIN")
#print(trading_history.groupby(by = trading_history.Result_string).count().Result)
trading_history.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/data_graf.xlsx")

trading_history.Date_closed = pd.to_datetime(trading_history.Date_closed)
trading_history.sort_values(by= "Date_closed", inplace= True)

import matplotlib.pyplot as plt
x = trading_history.Date_open
y = trading_history.Result

trading_history.drop(trading_history.index[0], inplace=True)

trading_history.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/data_graf.xlsx")


trading_history["hour"] = trading_history.Date_closed.apply(lambda x: x.hour)

trading_history.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/data_graf.xlsx")
hour_result_group = trading_history.groupby(by=["hour","Result_string"]).count().Result
test = trading_history.groupby(by=["hour", "Result_string"])[["Result_string"]] #single bracket = series, double = Dataframe
test_count_grouped = test.count()
hour_result_group.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/data_graf.xlsx")
"""
print(test_count_grouped.index)
print(test_count_grouped.index.levels[0])
print(test_count_grouped.head())
print(test_count_grouped)
"""
df_percenta = pd.DataFrame(columns=["WIN", "LOOSE"])

for i in test_count_grouped.index.levels[0]:
    try:
        win_percento = test_count_grouped.loc[i].loc["WIN"] / (test_count_grouped.loc[i].loc["WIN"]+test_count_grouped.loc[i].loc["LOOSE"])
        loose_percento = test_count_grouped.loc[i].loc["LOOSE"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
        dictionary = dict(zip(["WIN","LOOSE"], [win_percento[0],loose_percento[0]]))
        df_percenta.loc[i] = dictionary
        """percento_win = test_count_grouped.loc[i].loc["WIN"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
        percento_lose = test_count_grouped.loc[i].loc["LOOSE"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
        test_count_grouped.loc[i].loc["WIN"] = percento_win
        test_count_grouped.loc[i].loc["LOOSE"] = percento_lose"""
    except (IndexError,KeyError):
        pass
#print(test_count_grouped.tail())
df_percenta.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/percenta.xlsx")
#print(df_percenta)


bad_hours = [0,6,7,20,23,15,16,17]
#print(trading_history.shape)
#print(trading_history.groupby(by="hour").size())

import numpy as np

def vymaz_hodin(hodina):

    if hodina in bad_hours:
        return np.nan
    else:
        return int(hodina)
#Vysledok podla parov bez odstranenia hodin

bez_opt_pair_df = trading_history.groupby(["Pair","Result_string"]).count()[["Result"]]
bez_opt_pary_excel = pd.Series()
index = []
for i in bez_opt_pair_df.index.levels[0]:
    index.append(i)
    win_ratio = bez_opt_pair_df.loc[i].loc["WIN"][0]/(bez_opt_pair_df.loc[i].loc["LOOSE"][0] + bez_opt_pair_df.loc[i].loc["WIN"][0])
    bez_opt_pary_excel[i] = win_ratio
bez_opt_pary_excel.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/bez_opt_pary.xlsx")


print(bez_opt_pair_df)
print(type(bez_opt_pair_df))




trading_history.hour = trading_history.hour.apply(vymaz_hodin)
#print(trading_history)
#print(trading_history.shape)
trading_history.dropna(how="any",axis = 0, inplace = True)
#print(trading_history.groupby("Result_string").Date_open.count())
ciastocna_optimalizacia = trading_history[["Result","Result_string"]]
#print(ciastocna_optimalizacia)
ciastocna_optimalizacia.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/ciastocna_optimalizacia.xlsx")

#Vysledok podla parov s optimalizaciou hodin
po_opt_pair_df = trading_history.groupby(["Pair","Result_string"]).count()[["Result"]]
po_opt_pary_excel = pd.Series()
index = []
for i in po_opt_pair_df.index.levels[0]:
    index.append(i)
    win_ratio = po_opt_pair_df.loc[i].loc["WIN"][0]/(po_opt_pair_df.loc[i].loc["LOOSE"][0] + po_opt_pair_df.loc[i].loc["WIN"][0])
    po_opt_pary_excel[i] = win_ratio
po_opt_pary_excel.to_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/po_opt_pary.xlsx")
pairs = ["NZDUSD","USDCAD"]
trading_history["Pips"]= trading_history.apply(lambda x: abs(x.Open_price - x.Closed_price), axis = 1)

opt_pair = trading_history[trading_history.Pair.isin(pairs)]
print(opt_pair.groupby("Result_string").count().Result)
print(opt_pair[opt_pair.Result_string == "WIN"].Result.mean())
print(opt_pair[opt_pair.Result_string == "LOOSE"].Result.mean())
print(opt_pair.groupby("Result_string").Pips.mean())
print(opt_pair.groupby("Result_string").Pips.sum())
print(trading_history.groupby("Result_string").Pips.sum())
#results saved with graphs








