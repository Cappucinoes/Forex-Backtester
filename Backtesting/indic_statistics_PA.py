import pandas as pd
import datetime
import oandapyV20.endpoints.forexlabs as labs
from oandapyV20 import API
import datetime
accountID = "101-004-8194699-002" # define accID, stanalone variables so that we dont need to create them every time
access_token =  "0a504d77a452765e89fef14a396edbb5-926aa0288f617853dc8468faa10fe46d" # define api_token
client = API(access_token)
params = {
    "period":604800, #is 3 HOURS BEHIND CEST
    "instrument":"EUR_USD"
}
r = labs.Spreads(params= params)
client.request(r)
spread_data = r.response
avg_spread_data = spread_data["avg"]
min_spread_data = spread_data["min"]
max_spread_data = spread_data["max"]
data = dict([i for i in avg_spread_data])
spread_ser = pd.Series([i for i in data.values()], index=data.keys())
new_index = [datetime.datetime.utcfromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S') for i in spread_ser.index]
spread_ser.index = new_index #creates pd.Series with timestamp as index and avg spread as value
print(spread_ser)

df_hotovy = pd.read_excel(r"C:\Users\Mato\Desktop\Python-trading-Algo\Backtesting\df_backtest_feed.xlsx")
df_hotovy.time = pd.to_datetime(df_hotovy.time.apply(lambda x: x[:-11]))

spread_df = pd.DataFrame(data=avg_spread_data,columns=["time","avg_spread"])

spread_df["time"] = pd.to_datetime(spread_df.time)

print(spread_df)
print(df_hotovy.time.dtype)


# backtest_feed = pd.read_excel(r"C:\Users\Mato\Desktop\Python-trading-Algo-master\Backtesting\\vysledky_stats.xlsx")
# backtest_feed = backtest_feed.loc[:,"data":]
# backtest_feed.limit_order_time = pd.to_datetime(backtest_feed.limit_order_time)
# print(backtest_feed.data)








#mozeme na urcenie spreadu pouzit na jednej strane >= a z druhej <= a dostaneme interval v ktorom sme!!
#pri tejto metode musime spravit df obsahujuci spread este predtym ako skusame interval, nieje nutne ukladat ho do excelu
#bolo by fajn vlozit spread rovno do zakladneho data feedu z ktoreho sa rozoznavaju signaly, aby si tu hodnotu mohol obchod rovno zobrat
#treba dbat na to ze spread nas bude zaujimat iba pri SL alebo TP, nie pri oboch, treba skontrolovat

""" 
for i in avg_spread_data:
    cas = datetime.datetime.utcfromtimestamp(i[0]).strftime('%Y-%m-%d %H:%M:%S')
    print(cas,i[1])
"""
#pd.set_option('display.width', 320)
#pd.set_option("display.max_columns", 20)

#columns = ["Date_open", "Order_type", "Size", "Pair","Open_price", "SL", "TP", "Date_closed", "Closed_price"]
#trading_history = pd.read_excel(r"C:\Users\Mato\Desktop\Python-trading-Algo-master\Backtesting\\vysledky_stats.xlsx")

#trading_history = trading_history.loc[:,"data":]
#print(trading_history.columns)
"""
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

print(test_count_grouped.index)
print(test_count_grouped.index.levels[0])
print(test_count_grouped.head())
print(test_count_grouped)

df_percenta = pd.DataFrame(columns=["WIN", "LOOSE"])

for i in test_count_grouped.index.levels[0]:
    try:
        win_percento = test_count_grouped.loc[i].loc["WIN"] / (test_count_grouped.loc[i].loc["WIN"]+test_count_grouped.loc[i].loc["LOOSE"])
        loose_percento = test_count_grouped.loc[i].loc["LOOSE"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
        dictionary = dict(zip(["WIN","LOOSE"], [win_percento[0],loose_percento[0]]))
        df_percenta.loc[i] = dictionary
        #percento_win = test_count_grouped.loc[i].loc["WIN"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
        #percento_lose = test_count_grouped.loc[i].loc["LOOSE"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
        #test_count_grouped.loc[i].loc["WIN"] = percento_win
        #test_count_grouped.loc[i].loc["LOOSE"] = percento_lose
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
"""







