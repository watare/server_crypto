#importation des donnees order book en format json_data
#construction d'une dataframe
#rajout des colonnes volume total style somme execl
#rajout d'une colonne detection des walls
#enregistrement des donnees traitees dans data_treated.JSON 

import json
import pandas as pd
import numpy as np

with open('data_poloniex.json') as json_data:
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
#calcul du volume global et detection des walls
    dfbids['bidstotalvolume'] = dfbids['bidsvolume'].cumsum(axis = 0)
    dfasks['askstotalvolume'] = dfasks['asksvolume'].cumsum(axis = 0)

    comparator = lambda x: 1000 if x>0.1 else 0


    askstotal = dfasks['askstotalvolume'].iloc[-1]
    dfasks['askswall'] = dfasks['asksvolume'].multiply(1/askstotal)
    dfasks['askswall'] = dfasks['askswall'].apply(comparator)

    bidstotal = dfbids['bidstotalvolume'].iloc[-1]
    dfbids['bidswall'] = dfbids['bidsvolume'].multiply(1/bidstotal)
    dfbids['bidswall'] = dfbids['bidswall'].apply(comparator)


    #concatenation de bids et asks + reindexage
    dfall = pd.concat([dfbids,dfasks],ignore_index=True)
    dfall = dfall.sort_values(by=['value']).reset_index(drop = True).replace(0,value = np.nan)
    print(dfall)

    dfall.to_json("data_treated.json",orient = 'table',index = False)
