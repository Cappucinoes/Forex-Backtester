#RUN THIS MODUL SEPARATELY THAN RUN ORDER_MODUL
print("...............: INITIALIZING :...............")
import datetime
import time
import range_signal # initializes connection gate with 5M feed
import pandas as pd
import xlrd
from oandapyV20.endpoints import orders
accountID = range_signal.accountID
access_token = range_signal.access_token

def spusti_range_signal(): #if this function is called, request for 5M data df is sent
    range_signal.fire_up(accountID, access_token)

starttime = time.time()

def cistic(data_frame):

    data_frame = data_frame
    data_frame_ceny = data_frame.PRICE
    for i in range(df.shape[0]):

        try:
            if float(data_frame_ceny[i]) == float(data_frame_ceny[i+1]):
                data_frame.drop(data_frame.index[i], inplace= True)
        except :
            print("Signaly pre {} vycistene od duplicitnych objednavok, ulozene do df".format(sheet_name))

    #data_frame.to_excel(writer_signals,sheet_name) #SAVES READY SIGNAL INTO CSV SO THAT ORDER MODUL CAN PROCEED
    #writer_signals.save() # mozne je dat na koniec hlavneho while loopu
    return data_frame



if __name__ == "__main__":

    print("Refreshing active for every 60 seconds.")
    xlsx = xlrd.open_workbook("/Users/Cappucinoes/PycharmProjects/Bakalarka_PA/range_market_multi/df_hotovy.xlsx")
    while True:
        now = datetime.datetime.now().second
        writer_signals = pd.ExcelWriter("/Users/Cappucinoes/PycharmProjects/Bakalarka_PA/range_market_multi/signals.xlsx")
        if now == 1: #cakat sekundu na nahranie dat
            print("\n FIREEEEEEEEEEEEEEEEEEEEEEEEEEEEEE \n")
            spusti_range_signal()  # asks for data from 5M range_signal modul
            try:
                for sheet_name in xlsx.sheet_names(): # pre kazdy par v data feed exceli
                    print("Vyhladavam ordery pre {}".format(sheet_name))
                    signals = pd.read_excel("/Users/Cappucinoes/PycharmProjects/Bakalarka_PA/range_market_multi/df_hotovy.xlsx",sheet_name = sheet_name)["signal"] # najde stlpec signal pre aktualny par
                    signals = signals[pd.isnull(signals) == False]
                    columns = ["typ", "PRICE", "STOP_LOSS", "TAKE_PROFIT"]
                    data = [i.split(" ") for i in signals]
                    for i in data:
                        i.remove("SL")
                        i.remove("TP")
                    df = pd.DataFrame(data, columns= columns)
                    df_signaly_pre_par = cistic(data_frame = df)
                    df_signaly_pre_par.to_excel(writer_signals, sheet_name)
                writer_signals.save()
            except (ConnectionError) as error:
                print(error)
                pass

            print("Dataframe saved! Ready to be used with signals.xlsx, next data available in {} seconds".format(60 - datetime.datetime.now().second))
        #time.sleep(60.0 - ((time.time() - starttime)) % 60.0) # refresh every 60 seconds, needs to be 5mins

#FUNKCNE



#aktualizovane 12.4. na mac cesty