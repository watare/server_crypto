import json
import pandas as pd
import numpy as np
import sys
import os.path

homedir = os.path.expanduser("~")
montantinvesti = 50.000000000/7000.0000000000
montantdisponible = 50.0
valorisation = 0.0
donothing = 100.00/7000

with open(homedir + "/server_crypto/algosignal.json") as json_data:
    data_dict = json.load(json_data)
    json_data.close()
#transformation JSON en 2 dataframe
    algosignal = data_dict['algosignal']
    tlohcv = data_dict['tlohcv']


    #transformation en dictionnaire
    #ajout de la liste de dicitonnaire dans les dataframes
    dfalgosignal = pd.DataFrame(algosignal)
    dfalgosignal.columns = ['time','prix','tendance']
    dftlohcv = pd.DataFrame(tlohcv)

    dfalgotlohcv = dfalgosignal.merge(dftlohcv)
    dfalgotlohcv = dfalgotlohcv.sort_values(by=['time'],ascending=False).reset_index(drop = True)

    #df_algotlohcv = df_algotlohcv.sort_values(by=['time']).reset_index(drop = True)


    def compare(prix,tendance,close,valorisation = valorisation):
        global montantdisponible
        global montantinvesti

        if tendance == "bid":
            if close < prix:
                montantinvesti = montantinvesti + montantdisponible * float(1/close)
                montantdisponible = 0.0
                valorisation = montantdisponible + montantinvesti * close
            else :
                valorisation = montantdisponible + montantinvesti * close
        elif tendance == "ask":
            if close > prix:
                montantdisponible = montantdisponible + montantinvesti *close
                montantinvesti = 0.000000000000
                valorisation = montantdisponible + montantinvesti * close
            else :
                valorisation = montantdisponible + montantinvesti * close

        return [montantdisponible,montantinvesti,valorisation]

    data = dfalgotlohcv["close"].iloc[0]
    #print(1/data)
    dfalgotlohcv["montantdisponible"]= dfalgotlohcv.apply(lambda x: compare(x.prix,x.tendance,x.close)[0], axis=1)
    dfalgotlohcv["montantinvesti"]= dfalgotlohcv.apply(lambda x: compare(x.prix,x.tendance,x.close)[1], axis=1)
    dfalgotlohcv["valorisation"]= dfalgotlohcv.apply(lambda x: compare(x.prix,x.tendance,x.close)[2], axis=1)
    dfalgotlohcv["sans_opti"]=dfalgotlohcv.apply(lambda x :x.close*100.0/7000.0,axis=1)

    print(dfalgotlohcv)

    dfalgotlohcv.to_json(homedir+"/my-app/src/assets/algotlohcv.json",orient = 'table',index = False)#print(dftlohcv.head())
