import datetime
import time
import forex_bakalarka # initializes connection gate with 1M feed
import pandas as pd
import xlrd
from oandapyV20 import API
import ast
import json

accountID = forex_bakalarka.accountID
access_token = forex_bakalarka.access_token
second_algo_historia = []           # file do ktoreho sa ulozia objednavky aby nemal zdvojene

def spusti_range_signal(): #if this function is called, request for 5M data df is sent
    forex_bakalarka.fire_up(accountID, access_token)


def open_trade(SL, TP, typ, mena, units=2000):
    typ = typ.replace("''", "")
    mena = mena.replace("''", "")
    SL = str(round(float(SL), 5))
    TP = str(round(float(TP), 5))
    try:
        if typ == "SELL":
            units = -units

        elif typ == "BUY":
            units = units

        order_data = {
            "order": {
                "stopLossOnFill": {
                    "timeInForce": "GTC",
                    "price": str(SL)
                },
                "takeProfitOnFill": {
                    "timeInForce": "GTC",     #timeinForce je pridany riadok po novom 
                    "price": str(TP)
                },
                "timeInForce": "FOK",
                "instrument": str(mena),
                "units": str(units),
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }

        r = orders.OrderCreate(accountID=accountID, data=order_data)
        client.request(r)
        print("Objednavka otvorena {}".format(mena))
        second_algo_historia.append(mena)
        vsetky_identifikovane_objednavky = open("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/vsetky_identifikovane_objednavky.txt", "a+")
        vsetky_identifikovane_objednavky.write("{} {} \n".format(mena, datetime.datetime.now()))
        vsetky_identifikovane_objednavky.close()
        return second_algo_historia

    except Exception as Error:
        print(Error)
        print("TP je {}".format(TP), "Format TP je {}".format(type(TP)))
        pass



starttime = time.time()

import xlrd


forex_bakalarka.fire_up(accountID,access_token)
xlsx = xlrd.open_workbook("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/df_hotovy.xlsx")



import oandapyV20.endpoints.orders as orders  # sluzi na otvaranie pozicii
import oandapyV20.endpoints.trades as trades  # sledovanie aktualnych pozicii
client = API(access_token=access_token)

print("Refreshing active for every 60 seconds.")

while True:
    now = datetime.datetime.now().second
    minutes = datetime.datetime.now().minute

    if minutes in [a for a in range(0,60,10)]:
        second_algo_historia = []         # tuna sa ten file premaze kazdych 10 minut, az potom vie spravit na rovnakom pare
    else:
        pass

    if now == 1: # cakat tri sekundy, aktualne sviecky, aktualna minuta, je treba zmenit pri vyssom ramci
        spusti_range_signal() #asks for data from 5M range_signal modul
        print("Spusteny modul forex_bakalarka")

        try:
            for sheet_name in xlsx.sheet_names():

                print("Vyhladavam signaly pre {}.".format(sheet_name))
                signals = pd.read_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_Indic/second_algo/df_hotovy.xlsx",sheet_name)["EMA_CROSS"]
                if pd.isnull(signals[signals.index[-1]]) == False:
                    print("MAME SIGNAL NA {} {}".format(sheet_name, signals[signals.index[-1]]))

                    signal_str = signals[signals.index[-1]] # z tohto stringu potrebujeme dictionary aby sme ho mohli dat do jsonu a poslat na objednavku
                    signal_str = signal_str[1:-1].replace(":", "").strip().split(",")
                    values = [i.split()[1] for i in signal_str]
                    SL,TP,typ,mena = [i for i in values]
                    mena = sheet_name
                    print(type(SL),type(TP),type(typ),type(mena))

                    if mena not in second_algo_historia:
                        open_trade(SL,TP,typ,mena,units = 1000)
                        print("Aktualna cena je {}".format(forex_bakalarka.aktualna_cena_pre(mena)))
                    else:
                        print("ZABRANILO SA DVOJITEMU OBCHODU")

                else:
                    pass

        except (ConnectionError) as error:
            print(error)
            pass
        print("Hladanie skoncilo")
        #time.sleep(60.0 - ((time.time() 0- starttime)) % 60.0) # refresh every 60 seconds, needs to be 5mins

#saved on 12th of april, paths for mac