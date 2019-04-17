import pandas as pd
import datetime
import oandapyV20.endpoints.forexlabs as labs
from oandapyV20 import API



pd.set_option('display.width', 320)
pd.set_option("display.max_columns", 20)


trading_history = pd.read_excel(r"C:\Users\Cappucinoe`s Beast\Desktop\Python-Algo\Backtesting\vysledky_stats.xlsx")
trading_history = trading_history.loc[:,"Date_open":]
print(trading_history.head())
# ak dojde k odstraneniu casov alebo parov je potrebne ich zadat pred spustenim funkcie!!!


def uloz_df_na_graf(df,file_name):
    df.to_excel(r"C:\Users\Cappucinoe`s Beast\Desktop\Python-Algo\Backtesting\{}.xlsx".format(file_name))

def cas_win_lose(cas):
    results = trading_history.groupby([cas, "balance_effect"]).count().Result
    results_df = pd.DataFrame(columns=["WIN_RATIO", "LOOSE_RATIO"])
    for i in results.index.levels[0]:
        try:
            win_percento = results.loc[i].loc["TP_HIT"] / (
                    results.loc[i].loc["TP_HIT"] + results.loc[i].loc["SL_HIT"])
            loose_percento = results.loc[i].loc["SL_HIT"] / (
                    results.loc[i].loc["TP_HIT"] + results.loc[i].loc["SL_HIT"])
            dictionary = dict(zip(["WIN_RATIO", "LOOSE_RATIO"], [win_percento, loose_percento]))
            results_df.loc[i] = dictionary
            # percento_win = results.loc[i].loc["WIN"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
            # percento_lose = test_count_grouped.loc[i].loc["LOOSE"] / (test_count_grouped.loc[i].loc["WIN"] + test_count_grouped.loc[i].loc["LOOSE"])
            # test_count_grouped.loc[i].loc["WIN"] = percento_win
            # test_count_grouped.loc[i].loc["LOOSE"] = percento_lose
        except (IndexError, KeyError):
            pass

    uloz_df_na_graf(results_df, "WIN_RATIO_BY_{}".format(cas))
    print("Win ratio podla {} ulozene.".format(cas))



def vytvor_statistiku(trading_history):
    zoradene_datum_otvorenia = trading_history.sort_values(by= "Date_open")
    zoradene_datum_zatvorenia = trading_history.sort_values(by = "Date_closed")

    #WIN RATIO CELEJ STRATEGIE
    print("Celkovy pocet pipov pre L/W",trading_history.groupby(by = "balance_effect").Result.sum()) # pocet pipov W/L
    print(trading_history.groupby(by = "balance_effect").count().Result) # pomer lose win

    #currency win ratio
    stat = trading_history.groupby(by = ["Pair", "balance_effect"]).count().Result
    uloz_df_na_graf(stat, "neoptimalizovana_nospread_curr")
    print("Vysledne data pre graf na win ratio podla paru ulozene")

    #win ratio by time
    trading_history["hour"] = trading_history.Date_open.apply(lambda x: x.hour)
    cas_win_lose(cas="hour") #vytvori statisticke data pre ziskovost podla jednotlivych hodin



    #average win/loss in pips and AVG RRR
    stat = trading_history.groupby("balance_effect").mean().Result
    print("Priemerny pocet pipov pri stratovom obchode je ", stat[0])
    print("Priemerny pocet pipov pri ziskovom obchode je ", stat[1])
    avg_rrr = abs(stat[1]/stat[0])
    print("Priemerne risk-reward ratio je",avg_rrr,": 1")

    #WIN ratio podla buy/sell typu
    stat = trading_history.groupby(by = ["Order_type", "balance_effect"]).count().Result
    print("WIN RATIO PRE BUY JE ", (stat["BUY"]["TP_HIT"] / stat["BUY"]["SL_HIT"])*100, " percent")
    print("WIN RATIO PRE SELL JE ", (stat["SELL"]["TP_HIT"] / stat["SELL"]["SL_HIT"])*100, " percent")

    #average hold time
    dates_df = trading_history.apply(lambda x: x.Date_closed - x.Date_open , axis = 1)
    avg_hold_time = divmod(dates_df.mean().total_seconds(), 60)
    print("Average position hold time is {} minutes and {} seconds".format(str(avg_hold_time[0])[:-2], str(avg_hold_time[1])[:2]))

    #WIN RATIO PODLA DNI + pocet dni potrebnych na obchodovanie
    day_col = trading_history.Date_open.apply(lambda x: x.day)
    trading_history["day"] = day_col
    prvy_den = trading_history.day.iloc[0]
    posledny_den = trading_history.day.iloc[trading_history.shape[0]-1]
    print("Na obchodovanie bolo treba {} dni".format(posledny_den - prvy_den))
    cas_win_lose(cas = "day") #vytvori statisticke data pre ziskovost podla jednotlivych dni

    print("Win ratio podla obchodnych dni ulozene.")



vytvor_statistiku(trading_history)
"""  
bad_hours = [0,6,7,20,23,15,16,17]
import numpy as np
def vymaz_hodin(hodina):

    if hodina in bad_hours:
        return np.nan
    else:
        return int(hodina)

trading_history.hour = trading_history.hour.apply(vymaz_hodin)
trading_history.dropna(how="any",axis = 0, inplace = True)
#results saved with graphs
"""







