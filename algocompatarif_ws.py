import json
import pandas as pd
import numpy as np
import sys
import os.path

homedir = os.path.expanduser("~")
montantinvesti = 100.000000000/7000.0000000000
montantdisponible = 0
valorisation = 0.0
donothing = 100.00/7000

with open(homedir + "/server_crypto/data/algosignal_ws.json") as json_data:
    data_dict = json.load(json_data)
    json_data.close()
#transformation JSON en 2 dataframe
    algosignal = data_dict['algosignal']
    tlohcv = data_dict['tohlcv']


    #transformation en dictionnaire
    #ajout de la liste de dicitonnaire dans les dataframes
    dfalgosignal = pd.DataFrame(algosignal)
    dfalgosignal.columns = ['prix','tendance','time']
    dftlohcv = pd.DataFrame(tlohcv)
    print(dftlohcv.sort_values(by=['time'],ascending=False).reset_index(drop = True))
    print(dfalgosignal.sort_values(by=['time'],ascending=False).reset_index(drop = True))
    dfalgotlohcv = dfalgosignal.merge(dftlohcv)

    dfalgotlohcv = dfalgotlohcv.sort_values(by=['time'],ascending=False).reset_index(drop = True)

    #df_algotlohcv = df_algotlohcv.sort_values(by=['time']).reset_index(drop = True)


    def compare(prix,tendance,low,high,close,valorisation = valorisation):
        global montantdisponible
        global montantinvesti
#les colonnes open et low sont inversees
        if tendance == "bid":
            if open < prix:
                montantinvesti = montantinvesti + montantdisponible * float(1/prix)
                montantdisponible = 0.0
                valorisation = montantinvesti * close
            else :
                valorisation = montantdisponible + montantinvesti * close
        elif tendance == "ask":
            if high > prix:
                montantdisponible = montantdisponible + montantinvesti *prix
                montantinvesti = 0.000000000000
                valorisation = montantdisponible
            else :
                valorisation = montantdisponible + montantinvesti * close
        else:
            valorisation = montantdisponible + montantinvesti * close
        return [montantdisponible,montantinvesti,valorisation]

    #data = dfalgotlohcv["close"].iloc[0]
    #print(1/data)
    #dfalgotlohcv["montantdisponible"]= dfalgotlohcv.apply(lambda x: compare(x.prix,x.tendance,x.close)[0], axis=1)
    #dfalgotlohcv["montantinvesti"]= dfalgotlohcv.apply(lambda x: compare(x.prix,x.tendance,x.close)[1], axis=1)
    #dfalgotlohcv["valorisation"]= dfalgotlohcv.apply(lambda x: compare(x.prix,x.tendance,x.close)[2], axis=1)


    df_resultat = pd.DataFrame(columns = ["montantdisponible","montantinvesti","valorisation"])
    data_list =[]
    #inversion des lignes pour que l'algo parte bien du montantinvesti original
    dfalgotlohcv_r = dfalgotlohcv.iloc[::-1]
    for row in dfalgotlohcv_r.iterrows():
        resultat = compare(row[1].prix,row[1].tendance,row[1].low,row[1].high,row[1].close)
        #insertion de du resultat au debut pour reinverser le resultat
        data_list.insert(0,{"montantdisponible":resultat[0],"montantinvesti":resultat[1],"valorisation":resultat[2]})
        #print(row[1].prix)
    df2_resultat = df_resultat.append(data_list)

    dfalgotlohcv["dispo"] = df2_resultat["montantdisponible"]
    dfalgotlohcv["investi"] = df2_resultat["montantinvesti"]
    dfalgotlohcv["valor"] = df2_resultat["valorisation"]
    dfalgotlohcv["sans_opti"]=dfalgotlohcv.apply(lambda x :x.close*donothing,axis=1)
    dfalgotlohcv.drop_duplicates(subset = 'time',inplace=True)
    print(dfalgotlohcv)
    #dfalgotlohcv.to_json(homedir+"/my-app/src/assets/algotlohcv.json",orient = 'table',index = False)#print(dftlohcv.head())
