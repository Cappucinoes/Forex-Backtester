#TESTOVACI SCRIPT OD ORDER_MODUL
print("Order modul bezi.")
import oandapyV20
from oandapyV20 import API
import pandas as pd
import oandapyV20.endpoints.pricing as pricing
import configparser
from range_signal import accountID, access_token
import datetime
import xlrd

api = API(access_token=access_token)

# POSSIBILITY OF THREADING USAGE

open_file = open("/Users/Cappucinoes/PycharmProjects/Bakalarka_PA/range_market_multi/obchodna_historia.txt", "a")
open_file.close()


def get_actual_price(menovy_par):
    params = {"instruments": menovy_par}
    r = pricing.PricingInfo(accountID= accountID, params= params)
    rv = api.request(r)
    return rv["prices"][0]['bids'][0]["price"]

def order_ident(df_to_parse): # vezme df z aktualneho sheetu z for loopu
    order_type = []
    order_price = []
    order_sl = []
    order_tp = []
    for i in df_to_parse.iterrows():
        if "BUY" in i[1]["typ"]:

            if abs(float(i[1]["PRICE"]) - float(i[1]["STOP_LOSS"])) < 0.00030: #ak je stoploss prilis maly
                i[1]["STOP_LOSS"] = str(float(i[1]["STOP_LOSS"]) - 0.00030) #zvacsime stoploss o hodnotu

            if abs(float(i[1]["PRICE"]) - float(i[1]["TAKE_PROFIT"])) < 0.00030: #ak je take profit prilis maly
                i[1]["TAKE_PROFIT"] = str(float(i[1]["TAKE_PROFIT"]) + 0.00050) # zvacsime ho o ciastku

            order_type.append("BUY") # priradi hodnotu do listu
            order_price.append(i[1]["PRICE"])
            order_sl.append(i[1]["STOP_LOSS"])
            order_tp.append(i[1]["TAKE_PROFIT"])

        elif "SELL" in i[1]["typ"]:

            if abs(float(i[1]["PRICE"]) - float(i[1]["STOP_LOSS"])) < 0.00030:
                i[1]["STOP_LOSS"] = str(float(i[1]["STOP_LOSS"]) + 0.00030)

            if abs(float(i[1]["PRICE"]) - float(i[1]["TAKE_PROFIT"])) < 0.00030:
                i[1]["TAKE_PROFIT"] = str(float(i[1]["TAKE_PROFIT"]) - 0.00050)

            order_type.append("SELL")
            order_price.append(i[1]["PRICE"])
            order_sl.append(i[1]["STOP_LOSS"])
            order_tp.append(i[1]["TAKE_PROFIT"])
    return order_type,order_price,order_sl,order_tp #returns 4 lists with values


import oandapyV20.endpoints.orders as orders #sluzi na otvaranie pozicii
import oandapyV20.endpoints.trades as trades #sledovanie aktualnych pozicii

def get_actual_price(menovy_par):
    params = {"instruments": menovy_par}
    r = pricing.PricingInfo(accountID= accountID, params= params)
    rv = api.request(r)
    return rv["prices"][0]['bids'][0]["price"]

def open_limit_order(units,buy_or_sell, price, stop_loss, take_profit,instrument):
    if buy_or_sell == "SELL":
        units = -units

    order_data = {
        "order": {
            "price": str(price),
            "timeInForce": "GTC",
            "instrument": str(instrument),
            "units": str(units),
            "clientExtensions": {
                "comment": "Algo rulez bitch!"
            },
            "stopLossOnFill": {
                "timeInForce": "GTC",
                "price": str(stop_loss)
            },
            "takeProfitOnFill": {
                "price": str(take_profit)
            },
            "type": "MARKET_IF_TOUCHED",
            "positionFill": "DEFAULT"
        }
    }
    r = orders.OrderCreate(accountID=accountID, data = order_data)
    api.request(r)
    print(r.response, "\n VYTVORENA POZICIA")
    history_file.write(price)

def round_up(list_to_round): # funkcia pre zaokruhlenie
    rounded_list = []
    for i in list_to_round:
        rounded_list.append(str(round(float(i), 5)))
    return rounded_list

xlsx = xlrd.open_workbook("/Users/Cappucinoes/PycharmProjects/Bakalarka_PA/range_market_multi/signals.xlsx") # assigns opened excel with signals on all sheets

while True:  #
    for sheet_name in xlsx.sheet_names():
        df_for_order_ident = pd.read_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_PA/range_market_multi/signals.xlsx", sheet_name = sheet_name) #assigns one sheet to df so that order_ident can parse it
        order_type, order_price, order_sl, order_tp = order_ident(df_to_parse=df_for_order_ident) # vyziada si data vo forme listov / napr order_type je list so vsetkymi typmi #aktualne refreshovany every 5 mins
        actual_price = get_actual_price(menovy_par= sheet_name)
        order_price = round_up(order_price)
        order_sl = round_up(order_sl)
        order_tp = round_up(order_tp)
        order_instrument = sheet_name # sets currency for order

        with open("/Users/Cappucinoes/PycharmProjects/Bakalarka_PA/range_market_multi/obchodna_historia.txt", "r+") as history_file:
            obchodna_historia = history_file.read()

            for i in range(len(order_type)):
                if (order_type[i] == "BUY") and (order_price[i] not in obchodna_historia) and (float(actual_price) >= float(order_price[i])):
                    open_limit_order(2000,buy_or_sell= order_type[i],price = order_price[i], stop_loss= order_sl[i], take_profit= order_tp[i], instrument= order_instrument)

                elif (order_type[i] == "SELL") and (order_price[i] not in obchodna_historia) and (float(actual_price) <= float(order_price[i])): # PRIDAT PODMIENKU ACTUAL PRICE < ORDER_PRICE[I]
                    open_limit_order(2000, buy_or_sell= order_type[i],price = order_price[i], stop_loss= order_sl[i], take_profit= order_tp[i], instrument= order_instrument)

                else:
                    pass
    # NADCHADZAJUCI PROBLEM SA TYKA IDENTIFIKACIE OBCHODOV, TREBA TO TROSKU VYLADIT ABY BOLO VIAC MOZNOSTI NA TRADE


#aktualizovane 12.4. na mac cesty