#importation des donnees order book en format json_data
#construction d'une dataframe
#rajout des colonnes volume total style somme execl
#rajout d'une colonne detection des walls
#enregistrement des donnees traitees dans data_treated.JSON

import json
import pandas as pd
import numpy as np
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

    return [askstotal, bidstotal]
#tendance
    #achat/vente/nondefini
def tendance (askstotal,bidstotal,seuilvente = 50,seuilachat = 50):
    total = askstotal + bidstotal
    pourcentagevente = int(askstotal/total*100)
    pourcentageachat =  int(bidstotal/total*100)

    tendanceachat = False
    tendancevente = False
    tendancenondefinie = True

    if pourcentagevente  > seuilvente :
        tendancevente = True
        tendanceachat = False
        tendancenondefinie = False

    if pourcentageachat > seuilachat and tendancevente == False:
        tendanceachat = True
        tendancevente = False
        tendancenondefinie = False

    return [tendanceachat,tendancevente,tendancenondefinie]

#filtreBidsWall
def filtreBidsWall(dfbids):
    dfbids_filtre = dfbids.drop(dfbids[dfbids.bidswall == 1000].index)
    return dfbids_filtre

#filtreAsksWall
def filtreAsksWall(dfasks):
    dfasks_filtre = dfasks.drop(dfasks[dfasks.askswall == 1000].index)
    return dfasks_filtre

################################################################################
#algo

[dfbids,dfasks] = dataquisition("data_poloniex.json")
[askstotal,bidstotal] = calculVolumeGlobal(dfbids,dfasks)
tendavantfiltrage = tendance(askstotal,bidstotal,55,55)
print(tendavantfiltrage)

#filtrage
dfasks_filtre = filtreAsksWall(dfasks)
dfbids_filtre = filtreBidsWall(dfbids)
[askstotal_f,bidstotal_f] = calculVolumeGlobal(dfbids_filtre,dfasks_filtre)
tendance_f = tendance(askstotal_f,bidstotal_f,55,55)
print(tendance_f)

#fichier de sortie

#concatenation de bids et asks + reindexage
dfall = pd.concat([dfbids,dfasks],ignore_index=True,sort =True)
dfall = dfall.sort_values(by=['value']).reset_index(drop = True).replace(0,value = np.nan)

dfall_filtered = pd.concat([dfbids_filtre,dfasks_filtre],ignore_index=True,sort =True)
dfall_filtered = dfall_filtered.sort_values(by=['value']).reset_index(drop = True).replace(0,value = np.nan)
#suppression des walls



dfall_filtered.to_json("data_treated_filtered.json",orient = 'table',index = False)



dfall.to_json("data_treated.json",orient = 'table',index = False)
