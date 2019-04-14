import oandapyV20
from oandapyV20 import API
import pandas as pd
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import talib
import oandapyV20.endpoints.pricing as pricing
import configparser

accountID = "your_account_id" # define accID, stanalone variables so that we dont need to create them every time
access_token = "your_access_token" # define api_token
api = API(access_token) # initialize API
menove_pary = ["EUR_USD", "NZD_USD","USD_CHF","GBP_USD","AUD_USD","USD_CAD","GBP_CHF"] #list of currencies we wish to use

params = {"count":5000, # sets parameters for query
                "granularity": "M1"}
def fire_up(acc_id, access_t):
    accountID = acc_id # define accID
    access_token = access_t # define api_token


    writer = pd.ExcelWriter("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/df_backtest_feed.xlsx")

    for par in menove_pary: # bellow is a list of operations every sheet does

        data_set = instruments.InstrumentsCandles(instrument = par,params = params) # prepares the request
        api.request(data_set) #initialize request
        df = pd.DataFrame(data_set.response) #store fetched data into dataframe

        ohlc_list = ["o", "h", "l", "c"]  # support variable
        df_hotovy = pd.DataFrame(columns=["o", "h", "l", "c", "time", "type", "EMA_20", "candle_size_pip"],
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

            if df_hotovy.h[i] > df_hotovy.h[i + 1] and df_hotovy.h[i] > df_hotovy.h[i - 1] and df_hotovy.h[i] > df_hotovy.h[
                i - 2] and df_hotovy.h[i] > df_hotovy.h[i + 2]:
                swing_col[i] = "SWING_HIGH"
            elif df_hotovy.l[i] < df_hotovy.l[i + 1] and df_hotovy.l[i] < df_hotovy.l[i - 1] and df_hotovy.l[i] < df_hotovy.l[
                i - 2] and df_hotovy.l[i] < df_hotovy.l[i + 2]:
                swing_col[i] = "SWING_LOW"
            else:
                pass

        df_hotovy["EMA_20"] = talib.EMA(df_hotovy["c"], timeperiod=10)  # upraveny period z 20
        pd.set_option("display.float_format",
                      lambda x: "%.5f" % x)  # sets pandas number format for rounding to 0.000000
        df_hotovy["swing_col"] = swing_col
        # pouzijeme apply a series
        # RANGE IDENTIFIER
        # pocitanie vzdialenosti medzi swingami
        cislo_sviecky = 0
        highs = []
        lows = []
        indexy_pre_swing_high = []
        indexy_pre_swing_low = []

        for swing in df_hotovy["swing_col"]:
            if swing == "SWING_HIGH" or swing == "SWING_LOW":

                if swing == "SWING_HIGH":
                    highs.append(df_hotovy.h[cislo_sviecky])  # prida cenu high swingu do zoznamu 1. upper border
                    indexy_pre_swing_high.append(cislo_sviecky)


                elif swing == "SWING_LOW":
                    lows.append(df_hotovy.l[cislo_sviecky])  # prida cenu low swingu do zoznamu 2. bottom border
                    indexy_pre_swing_low.append(cislo_sviecky)

            cislo_sviecky += 1
        indexy_pre_swing_high = indexy_pre_swing_high[2:]  # sluzia na najdenie indexu riadka a nasledny concat s df_hotovy
        indexy_pre_swing_low = indexy_pre_swing_low[2:]

        # H a H swingove rozdiely
        highs_float = [float(x) for x in highs]
        highs_reversed_float = highs_float[-1::-1]  # od najnovsej ceny high_swingu po najstarsiu
        pd.Series(highs_float, index=[i for i in range(len(highs))]).plot()

        cena_high_swingu = []
        rozdiel_1_predosla_h = []
        rozdiel_2_predosla_h = []

        for cena_high in range(len(highs_reversed_float) - 2):
            cena_high_swingu.append(highs_reversed_float[cena_high])

            calc = highs_reversed_float[cena_high] - highs_reversed_float[cena_high + 1]
            rozdiel_1_predosla_h.append(abs(calc))

            calc = highs_reversed_float[cena_high] - highs_reversed_float[cena_high + 2]
            rozdiel_2_predosla_h.append(abs(calc))

        rozdiel_1_predosla_h = [round(x, 5) for x in rozdiel_1_predosla_h]
        rozdiel_2_predosla_h = [round(x, 5) for x in rozdiel_2_predosla_h]

        cena_high_swingu = pd.Series(cena_high_swingu)
        rozdiel_1_predosla = pd.Series(rozdiel_1_predosla_h)
        rozdiel_2_predosla = pd.Series(rozdiel_2_predosla_h)
        H_porovnanie_odnajnovsej = pd.concat(
            [cena_high_swingu, rozdiel_1_predosla, rozdiel_2_predosla, pd.Series(indexy_pre_swing_high[-1::-1])], axis=1)
        H_porovnanie_odnajnovsej.columns = ["cena_high_swingu", "rozdiel_1_predosla_h", "rozdiel_2_predosla_h",
                                            "indexy_pre_swing_high"]
        H_porovnanie_odnajstarsej = H_porovnanie_odnajnovsej.iloc[-1::-1]
        H_porovnanie_odnajstarsej.set_index("indexy_pre_swing_high", drop=True,
                                            inplace=True)  # porovnanie H swingov v rovnakom formate ako df_hotovy
        # H_porovnanie_odnajstarsej hotovy dataframe pre concat s df_hotovy
        df_hotovy = pd.concat([df_hotovy, H_porovnanie_odnajstarsej], axis=1)
        # L a L rozdiely
        cena_low_swingu = []
        rozdiel_1_predosla_l = []
        rozdiel_2_predosla_l = []
        lows_reversed_float = [float(x) for x in lows[-1::-1]]
         # musime pretocit na indexovanie flooru, potom nazad

        for cislo_operacie in range(len(lows_reversed_float) - 2):
            cena_low_swingu.append(lows_reversed_float[cislo_operacie])

            calc = abs(lows_reversed_float[cislo_operacie] - lows_reversed_float[cislo_operacie + 1])
            rozdiel_1_predosla_l.append(calc)

            calc = abs(lows_reversed_float[cislo_operacie] - lows_reversed_float[cislo_operacie + 2])
            rozdiel_2_predosla_l.append(calc)

        cena_low_swingu = pd.Series(cena_low_swingu)
        rozdiel_1_predosla_l = pd.Series(rozdiel_1_predosla_l)
        rozdiel_2_predosla_l = pd.Series(rozdiel_2_predosla_l)

        L_porovnanie_odnajnovsej = pd.concat(
            [cena_low_swingu, rozdiel_1_predosla_l, rozdiel_2_predosla_l, pd.Series(indexy_pre_swing_low[-1::-1])], axis=1)
        L_porovnanie_odnajnovsej.columns = ['cena_low_swingu', 'rozdiel_1_predosla_l', 'rozdiel_2_predosla_l',
                                            "indexy_pre_swing_low"]
        L_porovnanie_odnajnovsej.rozdiel_1_predosla_l.plot()
        L_porovnanie_od_najstarsej = L_porovnanie_odnajnovsej.iloc[-1::-1]
        L_porovnanie_od_najstarsej.set_index("indexy_pre_swing_low", drop=True,
                                             inplace=True)  # rozdiel medzi swing lowami, zoradene podla df_hotovy
        # L_porovnanie_od_najstarsej hotovy df na concat s df_hotovy
        df_hotovy = pd.concat([df_hotovy, L_porovnanie_od_najstarsej], axis=1)

        # Tento modul pocita rozdiely medzi H swingom a L swingom v pipoch
        # vacsia hodnota rozdielu = silnejsi trendovy pohyb
        highs_reversed = highs[-1::-1]
        lows_reversed = lows[-1::-1]

        list_rozdielov = []
        if len(highs_reversed) > len(lows_reversed):  # pripad kedy mame viac swing highov
            for i in range(len(lows_reversed)):
                rozdiel = abs(float(lows_reversed[i]) - float(highs_reversed[i]))
                list_rozdielov.append(rozdiel)

        elif len(highs_reversed) < len(lows_reversed):  # pripad kedy mame viac swing lowov
            for i in range(len(highs_reversed)):
                rozdiel = abs(float(lows_reversed[i]) - float(highs_reversed[i]))
                list_rozdielov.append(rozdiel)

        list_rozdielov = [round(x, 5) for x in list_rozdielov]

        import openpyxl
        # AVERAGE SIZE OF LAST 10 CANDLES
        avg_last_10 = []
        ceny = []

        for avg_period in range(10, df_hotovy.shape[0], 10):
            avg_period = int(avg_period)
            data = df_hotovy.candle_size_pip[(avg_period - 10): (avg_period)]
            avg = sum([i for i in dict(data).values()]) / len([i for i in dict(data).values()])
            avg_last_10.append(avg)
            ceny.append(df_hotovy.o[avg_period])

        avg_last_10 = pd.Series(avg_last_10, index=[i for i in range(10, df_hotovy.shape[0], 10)])
        df_hotovy["avg_last_10"] = avg_last_10

        # EMA FLATTER INDICATOR, treba ho reversnut asi
        index = []
        EMA_status = []
        for i in range(
                df_hotovy.shape[0] - (int(df_hotovy.columns[6][4:6]) + 1)):  # +1 alebo nie? porovnat hodnotu rozdielu v df

            rozdiel = abs(df_hotovy.EMA_20[df_hotovy.shape[0] - (1 + i)] - df_hotovy.EMA_20[df_hotovy.shape[0] - (2 + i)])
            if rozdiel <= 0.00002:
                EMA_status.append("EMA FLAT")
                index.append(df_hotovy.shape[0] - (1 + i))

        ema_series = pd.Series(EMA_status, index=index)[-1::-1]

        df_hotovy["FLAT_INDIC"] = ema_series

        # RANGE CEILING
        test_df = df_hotovy[["cena_high_swingu", "rozdiel_1_predosla_h", "rozdiel_2_predosla_h"]]
        test_df = test_df.iloc[-1::-1]

        roof_price = []
        roof_price_index = []
        pocitadlo = test_df.shape[0]

        for prvok in test_df.rozdiel_1_predosla_h:
            if pd.isnull(prvok) == False and prvok < 0.00009:
                roof_price.append(prvok)
                roof_price_index.append(pocitadlo - 1)
            pocitadlo -= 1

        roof_price_series = pd.Series(roof_price, index=roof_price_index)

        pocitadlo_2 = test_df.shape[0]

        for rozdiel in test_df.rozdiel_2_predosla_h:
            if pd.isnull(rozdiel) == False and rozdiel < 0.00009:

                if (pocitadlo_2 - 1) in roof_price_index and roof_price_series[pocitadlo_2 - 1] > rozdiel:
                    roof_price_series[pocitadlo_2 - 1] = rozdiel
                elif (pocitadlo_2 - 1) in roof_price_index and roof_price_series[pocitadlo_2 - 1] < rozdiel:
                    pass

                else:
                    roof_price_series[pocitadlo_2 - 1] = rozdiel

            pocitadlo_2 -= 1

        test_df["roof_price"] = roof_price_series

        def roof_price(index):
            test_df.roof_price[index] = test_df.cena_high_swingu[index]

        roof_price([i for i in roof_price_series.index])
        test_df = test_df["roof_price"]
        df_hotovy["roof_price"] = test_df

        # RANGE FLOOR MODUL
        test_df = df_hotovy[["cena_low_swingu", "rozdiel_1_predosla_l", "rozdiel_2_predosla_l"]]
        test_df = test_df.iloc[-1::-1]

        floor_price = []
        floor_price_index = []
        pocitadlo = test_df.shape[0]

        for prvok in test_df.rozdiel_1_predosla_l:
            if pd.isnull(prvok) == False and prvok < 0.00013:
                floor_price.append(prvok)
                floor_price_index.append(pocitadlo - 1)
            pocitadlo -= 1

        floor_price_series = pd.Series(floor_price, index=floor_price_index)

        pocitadlo_2 = test_df.shape[0]

        for rozdiel in test_df.rozdiel_2_predosla_l:
            if pd.isnull(rozdiel) == False and rozdiel < 0.00013:

                if (pocitadlo_2 - 1) in floor_price_index and floor_price_series[pocitadlo_2 - 1] > rozdiel:
                    floor_price_series[pocitadlo_2 - 1] = rozdiel
                elif (pocitadlo_2 - 1) in floor_price_index and floor_price_series[pocitadlo_2 - 1] < rozdiel:
                    pass

                else:
                    floor_price_series[pocitadlo_2 - 1] = rozdiel

            pocitadlo_2 -= 1

        test_df["floor_price"] = floor_price_series

        def floor_price(index):
            test_df.floor_price[index] = test_df.cena_low_swingu[index]

        floor_price([i for i in floor_price_series.index])
        test_df = test_df["floor_price"]
        df_hotovy["floor_price"] = test_df

        # PREDPOKLAD PRE VOID SVIECKU
        test_df = df_hotovy
        indexy = []
        hodnoty = []

        for i in range(test_df.shape[0]):
            if pd.isnull(test_df.swing_col[i]) == False:
                indexy.append(i)
                hodnoty.append(test_df.swing_col[i])

        swing_ser = pd.Series(hodnoty, index=indexy)

        indexy = indexy[-1::-1]
        swing_ser = swing_ser[-1::-1]  # otocit na lepsiu manipulaciu v loope (od najnovsieho po najstarsie)
        spodna_hranica = []
        index_pre_spodnu_hranicu = []

        for index_indexov in range(len(indexy)):
            if df_hotovy.roof_price[indexy[index_indexov]] > 0:
                for i in range(1, 6):

                    try:
                        if df_hotovy.swing_col[indexy[index_indexov + i]] == "SWING_LOW":
                            spodna_hranica.append(df_hotovy.l[indexy[index_indexov + i]])
                            index_pre_spodnu_hranicu.append(indexy[index_indexov])
                            break
                    except IndexError:
                        spodna_hranica.append("NaN")
                        index_pre_spodnu_hranicu.append(indexy[index_indexov])
                        break

        spodna_hranica_ser = pd.Series(spodna_hranica, index=index_pre_spodnu_hranicu)
        df_hotovy["spodna_hranica"] = spodna_hranica_ser

        horna_hranica = []
        index_pre_hornu_hranicu = []

        for index_indexov in range(len(indexy)):  # can be improved using functions together with the block above
            if df_hotovy.floor_price[indexy[index_indexov]] > 0:
                for i in range(1,6):

                    try:

                        if df_hotovy.swing_col[indexy[index_indexov + i]] == "SWING_HIGH":
                            horna_hranica.append(df_hotovy.h[indexy[index_indexov + i]])
                            index_pre_hornu_hranicu.append(indexy[index_indexov])
                            break

                    except IndexError:
                        horna_hranica.append("NaN")
                        index_pre_hornu_hranicu.append(indexy[index_indexov])
                        break

        horna_hranica_ser = pd.Series(horna_hranica, index=index_pre_hornu_hranicu)
        df_hotovy["horna_hranica"] = horna_hranica_ser

        swing_col = df_hotovy["swing_col"][pd.isnull(df_hotovy["swing_col"]) == False][-1::-1]

        #def oddelovac(sw_h_or_l):
        #    for index,value in swing_col.iteritems:
        #        if i == sw_h_or_l

        def prva_ema_rozdiel(h,l):
            rozdiel = h - l
            return abs(rozdiel)

        def spojovak(hranica, price):
            for ind in df_hotovy[pd.isnull(df_hotovy[hranica]) == False][price].index:
                df_hotovy.loc[ind, price] = float(df_hotovy.loc[ind, hranica])

        spojovak("horna_hranica", "roof_price")
        spojovak("spodna_hranica", "floor_price")

        df_hotovy.drop(["spodna_hranica",'horna_hranica'], axis=1, inplace = True)

        def ema_rozdiel(krok, indx_h, indx_l):
            if indx_h[krok - 1] < indx_l[krok - 1]:
                rozdiel = indx_h[krok - 1] - indx_l[krok]
                return abs(rozdiel)
            else:
                rozdiel = indx_l

        def closest_opposite_swing(ind, checked_candles):
            try:
                for next_candle in range(1, checked_candles + 1):
                    if swing_col[swing_col.index[ind + next_candle]] != swing_col[swing_col.index[ind]]:
                        ema_range = abs(swing_col.index[ind + next_candle] - swing_col.index[ind])
                        return ema_range
                        break

                    else:
                        pass
            except IndexError:
                pass

        def ema_flatter(ema_range):
            if pd.isnull(ema_range) == False and ema_range > 2:  # tu sa upravuje kolko sviecom musi mat range minimalne
                for pokus in range(ema_range + 1):
                    if pd.isnull(df_hotovy.FLAT_INDIC[swing_col.index[ind] - pokus]) == False:
                        validate = "RANGE_VALID"
                        validate_index = swing_col.index[ind]
                        return [validate, validate_index]
                        break

        def signal(valid_range_index, range_size, void_magnitude):  # dorobit void indic
            try:
                for i in range(1, 10):

                    if float(df_hotovy.c[valid_range_index + i]) > df_hotovy.roof_price[valid_range_index]:  # BUY SIGNAL
                        for potencial_void in range(5):
                            if df_hotovy.candle_size_pip[valid_range_index + i + potencial_void] > (
                                    range_size * void_magnitude):
                                signal = "BUY {} SL {} TP {} SC {}".format(df_hotovy.roof_price[valid_range_index], df_hotovy.floor_price[valid_range_index] - 0.00020,
                                                                     df_hotovy.roof_price[valid_range_index] + (abs(df_hotovy.roof_price[valid_range_index] - (df_hotovy.floor_price[valid_range_index] - 0.00020))) * 2.5,
                                                                           valid_range_index+i+potencial_void) #RRR set to 2.5:1
                                return [valid_range_index, signal]
                            break

                    elif float(df_hotovy.c[valid_range_index + i]) < df_hotovy.floor_price[valid_range_index]:
                        for potencial_void in range(5):
                            if df_hotovy.candle_size_pip[valid_range_index + i + potencial_void] > (
                                    range_size * void_magnitude):
                                signal = "SELL {} SL {} TP {} SC {}".format(df_hotovy.floor_price[valid_range_index], df_hotovy.roof_price[valid_range_index] + 0.00020,
                                                                      df_hotovy.floor_price[valid_range_index] - (abs(df_hotovy.floor_price[valid_range_index] - (df_hotovy.roof_price[valid_range_index] + 0.00020)))*2.5,
                                                                            valid_range_index + i + potencial_void) #RRR set to 2.5:1
                                return [valid_range_index, signal]
                            break

            except (IndexError, KeyError):
                pass

        signal_value = []
        signal_index = []
        for ind in range(len(swing_col.index)):
            if float(df_hotovy.roof_price[swing_col.index[ind]]) > 0:
                ema_range = closest_opposite_swing(ind, checked_candles=5)
                validate = ema_flatter(ema_range)

                if isinstance(validate, list) == True:
                    range_size = float(df_hotovy.roof_price[validate[1]]) - float(df_hotovy.floor_price[validate[1]])

                    signalik = signal(validate[1], range_size, 1.15)
                    if isinstance(signalik, list):
                        signal_value.append(signalik[1])
                        signal_index.append(signalik[0])

        signal_ser = pd.Series(signal_value, index=signal_index)
        df_hotovy["signal"] = signal_ser
        df_hotovy.to_excel(writer,par)
    writer.save()# NOT INDENTED

    print("Success! Multiple currency DF saved.")
# DATA FEED FUNCTIONAL, DATA HAVE TO BE CHACKED THO
#fire_up(accountID,access_token) - natiahne si sviecky 5k

def cistic(data_frame,sheet_name):
    data_frame = data_frame
    print("Zahajujem odstranovanie duplicit")
    data_frame_ceny = data_frame.PRICE
    for i in range(data_frame_ceny.shape[0]):
        try:
            if data_frame_ceny[data_frame_ceny.index[i]] == data_frame_ceny[data_frame_ceny.index[i+1]]:
                data_frame.drop(data_frame_ceny.index[i+1], inplace= True)

        except IndexError:
            print("Duplicity odstranene!")

            #print("Signaly pre {} vycistene od duplicitnych objednavok, ulozene do df".format(sheet_name))

    #data_frame.to_excel(writer_signals,sheet_name) #SAVES READY SIGNAL INTO CSV SO THAT ORDER MODUL CAN PROCEED
    #writer_signals.save() # mozne je dat na koniec hlavneho while loopu
    return data_frame

import xlrd

def vytvor_signal_excel_file(): # v tejto funkcii musi byt chyba
    xlsx = xlrd.open_workbook("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/df_backtest_feed.xlsx")

    writer_signals = pd.ExcelWriter("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/signals.xlsx")
    try:
        for sheet_name in xlsx.sheet_names():  # pre kazdy par v data feed exceli
            print("Vyhladavam ordery pre {}".format(sheet_name))
            signals = pd.read_excel("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/df_backtest_feed.xlsx", sheet_name=sheet_name)["signal"]  # najde stlpec signal pre aktualny par
            signals = signals[pd.isnull(signals) == False]
            columns = ["typ", "PRICE", "STOP_LOSS", "TAKE_PROFIT", "IDENTIFICATOR_CANDLE"]
            data = [i.split(" ") for i in signals]
            for i in data:
                i.remove("SL")
                i.remove("TP")
                i.remove("SC")
            df = pd.DataFrame(data, columns=columns, index= signals.index)
            df_signaly_pre_par = cistic(data_frame=df,sheet_name= sheet_name)
            df_signaly_pre_par.to_excel(writer_signals, sheet_name)
        writer_signals.save()
    except (ConnectionError) as error:
        print(error)
        pass

    print("Dataframe saved! Ready to be used with signals.xlsx")

import operator

def vyhodnotenie_signalu(data_df, signal_type,signal_price,signal_sl,signal_tp,signal_index, signal_identified_index):
    data_df_iter = data_df.iterrows()
    for row in data_df_iter:
        data_df_row_index = row[0]
        index_condition = operator.gt(data_df_row_index,signal_index) # hlada az od indexu orderu

        if index_condition: #ak je index iteracie od orderu mozeme pokracovat
            if signal_type == "BUY": #urci kontrolu TP a SL pre buy order
                check_tp = operator.ge(data_df["h"][data_df_row_index], signal_tp)
                check_sl = operator.le(data_df["l"][data_df_row_index], signal_sl)
                def check_open():
                    for index_kontrola_open in range(signal_identified_index+1, data_df_row_index):
                        if data_df["l"][index_kontrola_open] <= signal_price:
                            return True

            elif signal_type == "SELL": #urci kontrolu TP a SL pre sell order
                check_tp = operator.le(data_df["l"][data_df_row_index], signal_tp)
                check_sl = operator.ge(data_df["h"][data_df_row_index], signal_sl)
                def check_open():
                    for index_kontrola_open in range(signal_identified_index+1, data_df_row_index):
                        if data_df["h"][index_kontrola_open] >= signal_price:
                            return True
# funkcia check_open() skontroluje ci bol obchod vobed otvoreny v range LIMIT - SL/TP, ak ano vrati True

            if check_tp and check_open(): #ak cena dosiahla TP (resp. ak by bola pozicia uzavreta) a ak poziciu otvorilo

                vysledok = "{} ZACIATOK_POZICIE {} {} {} TP_HIT {} {}".format(data_df["time"][signal_index],signal_type, signal_index,signal_price, data_df_row_index, signal_tp)
                print("Cena otvorenia {} {} TP_HIT {}".format(signal_type,signal_price, signal_tp))
                return vysledok
                break

            elif check_sl and check_open(): #ak cena dosiahla SL (resp. ak by bola pozicia uzavreta) a ak poziciu otvorilo
                vysledok = "{} ZACIATOK_POZICIE {} {} {} SL_HIT {} {}".format(data_df["time"][signal_index],signal_type, signal_index, signal_price, data_df_row_index,signal_sl)
                print("Cena otvorenia {} {} SL_HIT {}".format(signal_type, signal_price, signal_sl))
                return vysledok
                break
            else:
                pass

def itteruj():
    vysledky_sorted = pd.DataFrame()
    writer_vysledky = pd.ExcelWriter("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/vysledky.xlsx")
    xlsx = xlrd.open_workbook("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/df_backtest_feed.xlsx")
    for sheet_name in xlsx.sheet_names():
        vysledok = []
        signal_df = pd.read_excel("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/pysignals.xlsx", sheet_name)
        data_df = pd.read_excel("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/df_backtest_feed.xlsx", sheet_name)
        signal_generator = signal_df.iterrows()
        for signal_row in signal_generator:
            signal_index = signal_row[0]
            signal_type = signal_row[1]["typ"]
            signal_price = signal_row[1]["PRICE"]
            signal_sl = signal_row[1]["STOP_LOSS"]
            signal_tp = signal_row[1]["TAKE_PROFIT"]
            signal_identified_index = signal_row[1]["IDENTIFICATOR_CANDLE"]

            vysledok.append(vyhodnotenie_signalu(data_df=data_df, signal_type = signal_type, signal_price = signal_price,
                                 signal_sl = signal_sl, signal_tp = signal_tp,signal_index = signal_index, signal_identified_index = signal_identified_index))
        ser = pd.Series(vysledok)
        ser.dropna(inplace=True)
        ser.to_excel(writer_vysledky, sheet_name)
        vysledky_sorted = pd.concat([vysledky_sorted, ser], ignore_index= True)
    writer_vysledky.save()
    vysledky_sorted.to_excel("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/vysledky_sorted.xlsx")

fire_up(accountID,access_token) # fetches data into file
vytvor_signal_excel_file() # creates supp files
itteruj() # does condition checking

def plus_minus(riadok):
    for i in riadok.split():
        if i == "SL_HIT" or i == "TP_HIT":
            return i

def extract_price(riadok, index_ceny): # index ceny je index riadku.split napr. pre open je 3
    return riadok.split()[index_ceny]


def vysledok_v_pip(riadok):
    vysledok_v_pip = abs(riadok["order_open_price"] - riadok["order_close_price"])
    if riadok["balance_effect"] == "TP_HIT":
        return vysledok_v_pip
    else:
        return -vysledok_v_pip

def spracuj_vysledky():
    vysledky_df = pd.read_excel("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/vysledky_sorted.xlsx")
    vysledky_df.columns = ["data"]
    vysledky_df["balance_effect"] = vysledky_df.data.apply(plus_minus)
    vysledky_df["order_open_price"] = vysledky_df.data.apply(extract_price,index_ceny=4) # index ceny = na akej pozicii indexu sa nachadza pozadovana cena
    vysledky_df["order_close_price"] = vysledky_df.data.apply(extract_price,index_ceny=7)
    #vysledky_df["vysledky_v_pip"] = vysledky_df.apply(vysledok_v_pip, axis=1)
    vysledky_df["order_close_price"] = vysledky_df["order_close_price"].apply(lambda x: float(x))
    vysledky_df["order_open_price"] = vysledky_df["order_open_price"].apply(lambda x: float(x))
    vysledky_df["vysledok_v_pip"] = vysledky_df.apply(vysledok_v_pip, axis= 1)
    vysledky_df["limit_order_time"] = vysledky_df.data.apply(lambda x: x.split()[0])

    return vysledky_df

import numpy as np
desired_width = 320
pd.set_option('display.width',desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',10)

vysledky_df = spracuj_vysledky()
print(vysledky_df.groupby(by =["balance_effect"]).count())
print(vysledky_df.tail())
#print(vysledky_df[["order_close_price","order_open_price","vysledok_v_pip", "balance_effect"]])
#print(vysledky_df["vysledok_v_pip"].sum)
vysledky_df.to_excel("/Users/Cappucinoes/PycharmProjects/Forex-Backtester/vysledky_stats.xlsx")

print(vysledky_df["vysledok_v_pip"].apply(lambda x: abs(x)).mean)
#cesty prepisane

#edit



