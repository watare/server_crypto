#importation des donnees order book en format json_data
#construction d'une dataframe
#rajout des colonnes volume total style somme execl
#rajout d'une colonne detection des walls
#enregistrement des donnees traitees dans data_treated.JSON

import json
import pandas as pd
import numpy as np
import sys
import os.path
homedir = os.path.expanduser("~")
################################################################################
                                #fonctions
################################################################################
#lecture du fichier JSON
def dataquisition(data):
    with open(data) as json_data:
        data_dict = json.load(json_data)
        json_data.close()
    #transformation JSON en 2 dataframe
        bids = data_dict['bids']
        asks = data_dict['asks']

        listbids = []
        listasks = []

        #transformation en dictionnaire
        for bid in bids :
            listbids.append({'value' : float(bid[0]), 'bidsvolume' :float(bid[1])})
        for ask in asks :
            listasks.append({'value' : float(ask[0]), 'asksvolume' :float(ask[1])})

        #ajout de la liste de dicitonnaire dans les dataframes
        dfbids = pd.DataFrame(listbids)
        dfasks = pd.DataFrame(listasks)
        return [dfbids,dfasks]

#calcul des volumes vente et achat
def calculVolumeGlobal (dfbids,dfasks):
    #calcul du volume global et detection des walls
    dfbids['bidstotalvolume'] = dfbids['bidsvolume'].cumsum(axis = 0)
    dfasks['askstotalvolume'] = dfasks['asksvolume'].cumsum(axis = 0)
    #le 0.1 correspond a 10% du volume global
    comparator = lambda x: 1000 if x>0.1 else 0


    askstotal = dfasks['askstotalvolume'].iloc[-1]
    dfasks['askswall'] = dfasks['asksvolume'].multiply(1/askstotal)
    dfasks['askswall'] = dfasks['askswall'].apply(comparator)

    bidstotal = dfbids['bidstotalvolume'].iloc[-1]
    dfbids['bidswall'] = dfbids['bidsvolume'].multiply(1/bidstotal)
    dfbids['bidswall'] = dfbids['bidswall'].apply(comparator)

    return [bidstotal, askstotal]
#tendance
    #achat/vente/nondefini
def tendance (bidstotal,askstotal,seuilvente = 51,seuilachat = 51):
    TACHAT = 1
    TVENTE = 2
    TUNDEFINED = 3
    total = askstotal + bidstotal
    pourcentagevente = int(askstotal/total*100)
    pourcentageachat =  int(bidstotal/total*100)

    _tendance = TUNDEFINED

    if pourcentagevente  > seuilvente :
        _tendance = TVENTE
    if pourcentageachat > seuilachat and _tendance != TVENTE:
        _tendance = TACHAT

    return _tendance

#filtreWall
def filtreWall(df,type):
    if (type == "bids"):
        dfbids_filtre = df.drop(df[df.bidswall == 1000].index)
        return dfbids_filtre
    if (type == "asks"):
        dfasks_filtre = df.drop(df[df.askswall == 1000].index)
        return dfasks_filtre
    else : print("erreur")

#placement_ordre
def placement_ordre(tendance,dfbids,dfasks):
    TACHAT = 1
    TVENTE = 2
    TUNDEFINED = 3

    def fAchat():
        dwall = dfbids.drop(dfbids[dfbids.bidswall != 1000].index)
        dwall = dwall.sort_values(by = 'value')
        #print dwall
        dwall = dwall["value"].iloc[-1]
        return ["bid",float(dwall)+0.00000001]

    def fVente():
        dwall = dfasks.drop(dfbids[dfasks.askswall != 1000].index)
        dwall = dwall.sort_values(by = 'value')
        dwall = dwall["value"].iloc[0]
        return ["ask",float(dwall)-0.00000001]


    def fRien():
        return ["undefined",-1.0]

    switcher={
        TVENTE: fVente,
        TACHAT: fAchat,
        TUNDEFINED: fRien
        }
    func = switcher.get(tendance, lambda: "argumentinvalide")
    return func()

################################################################################
                                #programme
################################################################################
if __name__ == '__main__':

    #aquisition des donnees
    [dfbids,dfasks] = dataquisition(homedir+"/server_crypto/data_received_gdax.json")
    #ajout des wall
    [askstotal,bidstotal] = calculVolumeGlobal(dfbids,dfasks)
    #print(dfbids)
    tendavantfiltrage = tendance(bidstotal,askstotal,50,50)
    #print(tendavantfiltrage)

    #filtrage des wall
    dfasks_filtre = filtreWall(dfasks,"asks")
    dfbids_filtre = filtreWall(dfbids,"bids")
    #tendance
    [askstotal_f,bidstotal_f] = calculVolumeGlobal(dfbids_filtre,dfasks_filtre)
    tendance_f = tendance(bidstotal_f,askstotal_f,50,50)

    #renvoi un tuple contenant l'action a executer (vendrvalorisation.pye/acheter/rien)
    #ainsi que prix a rentrer

    [_tendance, _prix] = placement_ordre(tendavantfiltrage,dfbids,dfasks)

    ##################################################################################
    #sauvegarde de l'algo

    import time
    now = int(time.time())
    date = now-now%60

    exists = os.path.isfile(homedir +'/server_crypto/algosignal.json')
    def dataAlgo(_tendance,_prix):
        if exists:
            with open(homedir +'/server_crypto/algosignal.json', 'r') as json_algo:
                    algosignal = json.load(json_algo)
                    algosignal["algosignal"].append({"tendance":_tendance,"prix":_prix,"date":date})
                    json_algo.close()
                    with open(homedir +'/server_crypto/algosignal.json', 'w') as json_algo:
                        json.dump(algosignal, json_algo)
                        json_algo.close()
                        #ajouter un element au fichier avec la date  la tendnace et le prix
        else:
            with open(homedir +'/server_crypto/algosignal.json', 'w') as json_algo:
                algosignal = {"algosignal":[{"tendance":_tendance,"prix":_prix,"date":date}]}
                json.dump(algosignal, json_algo)
                json_algo.close()

    def mergetlohcv():
        dates =[]
        match_tlohcv=[]
        with open(homedir +'/server_crypto/algosignal.json', 'r') as data_lohcv:
            _signal = json.load(data_lohcv)
            for date in _signal["algosignal"]:
                dates.append(date['date'])
            with open(homedir +'/server_crypto/data_received_tlohcv.json', 'r') as data_lo:
                tlohc = json.load(data_lo)
                for ele in tlohc:
                    if ele["time"] in dates:
                        match_tlohcv.append(ele)
                data_lo.close()
            data_lohcv.close()
            with open(homedir +'/server_crypto/algosignal.json', 'w') as data_l:
                _signal["tlohcv"] = match_tlohcv
                print match_tlohcv
                json.dump(_signal,data_l)

    ################################################################################
    dataAlgo(_tendance,_prix)
    mergetlohcv()
    #Affichage des donnees
    ################################################################################

    #concatenation de bids et asks + reindexage
    dfall = pd.concat([dfbids,dfasks],ignore_index=True,sort =True)
    dfall = dfall.sort_values(by=['value']).reset_index(drop = True).replace(0,value = np.nan)

    dfall_filtered = pd.concat([dfbids_filtre,dfasks_filtre],ignore_index=True,sort =True)
    dfall_filtered = dfall_filtered.sort_values(by=['value']).reset_index(drop = True).replace(0,value = np.nan)
    #suppression des walls



    dfall_filtered.to_json(homedir+"/my-app/src/assets/data_treated_filtered.json",orient = 'table',index = False)

    dfall.to_json(homedir+"/my-app/src/assets/data_treated.json",orient = 'table',index = False)


    sys.exit()
