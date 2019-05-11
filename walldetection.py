#importation des donnees order book en format json_data
#construction d'une dataframe
#rajout des colonnes volume total style somme execl
#rajout d'une colonne detection des walls
#enregistrement des donnees traitees dans data_treated.JSON

import json
import pandas as pd
import numpy as np

################################################################################
                                #fonctions
################################################################################
#lecture du fichier JSON
def dataquisition(data):
    with open(data) as json_data:
        data_dict = json.load(json_data)

    #transformation JSON en 2 dataframe
        bids = data_dict['bids']
        asks = data_dict['asks']

        listbids = []
        listasks = []

        #transformation en dictionnaire
        for bid in bids :
            listbids.append({'value' : bid[0], 'bidsvolume' :bid[1]})
        for ask in asks :
            listasks.append({'value' : ask[0], 'asksvolume' :ask[1]})

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
def tendance (bidstotal,askstotal,seuilvente = 50,seuilachat = 50):
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
        return dwall

    def fVente():
        dwall = dfasks.drop(dfbids[dfasks.askswall != 1000].index)
        dwall = dwall.sort_values(by = 'value')
        dwall = dwall["value"].iloc[0]
        return dwall


    def fRien():
        return -1

    switcher={
        TVENTE: fVente,
        TACHAT: fAchat,
        TUNDEFINED: fRien
        }
    func = switcher.get(tendance, lambda: "argumentinvalide")
    return float(func())

################################################################################
                                #programme
################################################################################

#aquisition des donnees
[dfbids,dfasks] = dataquisition("data_poloniex.json")
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


placement_ordre(tendavantfiltrage,dfbids,dfasks)
#print dfbids
#print(tendavantfiltrage)
#fichier de sortie

#concatenation de bids et asks + reindexage
dfall = pd.concat([dfbids,dfasks],ignore_index=True,sort =True)
dfall = dfall.sort_values(by=['value']).reset_index(drop = True).replace(0,value = np.nan)

dfall_filtered = pd.concat([dfbids_filtre,dfasks_filtre],ignore_index=True,sort =True)
dfall_filtered = dfall_filtered.sort_values(by=['value']).reset_index(drop = True).replace(0,value = np.nan)
#suppression des walls



dfall_filtered.to_json("../my-app/src/assets/data_treated_filtered.json",orient = 'table',index = False)



dfall.to_json("../my-app/src/assets/data_treated.json",orient = 'table',index = False)
