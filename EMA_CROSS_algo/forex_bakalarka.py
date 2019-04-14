import oandapyV20
from oandapyV20 import API
import pandas as pd
import oandapyV20.endpoints.pricing as pricing
import configparser
import talib
from pandas import ExcelWriter
import oandapyV20.endpoints.instruments as instruments

accountID = "101-004-8194699-002" # define accID, stanalone variables so that we dont need to create them every time
access_token = "0a504d77a452765e89fef14a396edbb5-926aa0288f617853dc8468faa10fe46d" # define api_token
menove_pary = ["EUR_USD", "NZD_USD","USD_CHF","GBP_USD","AUD_USD","USD_CAD","GBP_CHF"]
api = API(access_token = access_token) # initialize API

def aktualna_cena_pre(par):  # najde akutalnu cenu pre dany menovy par, sluzi na TP a SL

    import oandapyV20.endpoints.pricing as pricing
    params = {"instruments": str(par)}
    data_filter = pricing.PricingInfo(accountID=accountID,
                                      params=params)  # specifies values to call from request
    req_prices = api.request(data_filter)  # calls request, fetches data
    fetched_data = data_filter.response  # assigns fetched data to variable actual price, not needed
    cena = fetched_data["prices"][0]["bids"][0]["price"]
    return float(cena)


def fire_up(acc_id, access_t):
    df_hotovy = pd.DataFrame()
    accountID = acc_id # define accID
    access_token = access_t # define api_token


    params = {"count":100, # sets parameters for query
              "granularity": "M1"}
    writer = pd.ExcelWriter("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/df_hotovy.xlsx")
    for par in menove_pary:
        data_set = instruments.InstrumentsCandles(instrument = par,params = params) # prepares the request
        candle_data_request = api.request(data_set) #initialize request
        df = pd.DataFrame(data_set.response) #store fetched data into dataframe
        ohlc_list = ["o", "h", "l", "c"]  # support variable
        df_hotovy = pd.DataFrame(columns=["o", "h", "l", "c", "time", "type", "EMA_13", "EMA_50", "candle_size_pip"],
                                 index=[i for i in range(df.candles.shape[0])])

        for i in range(df.candles.shape[0]):
            for w in ohlc_list:  # for every open, high, low, close in i row
                df_hotovy[w][i] = df.candles[i].get("mid").get(w)  # ohlc columns into df
                df_hotovy["time"][i] = df.candles[i].get("time")  # time column into df


            if df_hotovy["c"][i] > df_hotovy["o"][i]:
                df_hotovy["type"][i] = "bullish"  # if cena close > open = bullish

            elif df_hotovy["c"][i] < df_hotovy["o"][i]:
                df_hotovy["type"][i] = "bearish"  # opak vrchneho if

            else:
                df_hotovy["type"][i] = "neutral"

            df_hotovy["candle_size_pip"][i] = abs(
                float(df_hotovy["h"][i]) - float(df_hotovy["l"][i]))  # calculate size of the bullish candle
        swing_col = pd.Series(index=range(1, df_hotovy.shape[0] - 2))

        for i in range(2, df_hotovy.shape[0] - 2):

            if df_hotovy.h[i] > df_hotovy.h[i + 1] and df_hotovy.h[i] > df_hotovy.h[i - 1] and df_hotovy.h[i] > \
                    df_hotovy.h[
                        i - 2] and df_hotovy.h[i] > df_hotovy.h[i + 2]:
                swing_col[i] = "SWING_HIGH"
            elif df_hotovy.l[i] < df_hotovy.l[i + 1] and df_hotovy.l[i] < df_hotovy.l[i - 1] and df_hotovy.l[i] < \
                    df_hotovy.l[
                        i - 2] and df_hotovy.l[i] < df_hotovy.l[i + 2]:
                swing_col[i] = "SWING_LOW"
            else:
                pass
        df_hotovy["SWING"] = swing_col

        df_hotovy["EMA_13"] = talib.EMA(df_hotovy["c"], timeperiod=13)
        df_hotovy["EMA_50"] = talib.EMA(df_hotovy["c"], timeperiod=50)

        cross_index = []
        cross_value = []
        for i,a in df_hotovy.iterrows():

            if (a["EMA_13"] < a["EMA_50"]) and (df_hotovy["EMA_13"][i-1] > df_hotovy["EMA_50"][i-1]):
                cena = aktualna_cena_pre(par)
                cross_index.append(i)
                cross_value.append({"SL":cena+0.00050,
                                "TP":cena-0.00100,
                                "TYPE":"SELL",
                                    "PAIR":par})

            elif (a["EMA_13"] > a["EMA_50"]) and (df_hotovy["EMA_13"][i-1] < df_hotovy["EMA_50"][i-1]):
                cena = aktualna_cena_pre(par)
                cross_index.append(i)
                cross_value.append({"SL":cena-0.00050,
                                "TP":cena+0.00100,
                                "TYPE":"BUY",
                                    "PAIR":par})

            else:
                pass
        cross_ser = pd.Series(cross_value, index=cross_index)

        df_hotovy["EMA_CROSS"] = cross_ser


        df_hotovy.to_excel(writer, par)
    writer.save()
    print("Data ulozene!")

#saved on 12th of april, paths for MAC
