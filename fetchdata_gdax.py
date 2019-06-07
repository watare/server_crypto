import cbpro
import json
import sys
import os.path
homedir = os.path.expanduser("~")

def fetchdata():
    #reception des donnees orderbook gdax et stockage dans un fichier
    public_client = cbpro.PublicClient()
    with open(homedir +'/server_crypto/data/data_received_gdax.json', 'w') as f:
        data = public_client.get_product_order_book('BTC-EUR', level=2)
        data = json.dumps(data)
        f.write(data)
        f.close()

    data = public_client.get_product_historic_rates('BTC-EUR', granularity=60,start = "2019-06-01")
    #print(data)
    listdata = []
    for da in data:
        da[0] = da[0] - da[0]%60
        listdata.append({'time' :da[0], 'open' :da[1],'high':da[2],'low':da[3],'close':da[4],'volume':da[5]})
    with open(homedir +'/server_crypto/data/data_received_tlohcv.json', 'r') as fold:
        data_dict = json.load(fold)
        listdata = listdata + data_dict
        listdata = [i for n, i in enumerate(listdata) if i not in listdata[n + 1:]]
        print (listdata)
        fold.close()
    with open(homedir +'/server_crypto/data/data_received_tlohcv.json', 'w') as f:
        json.dump(listdata,f)
        f.close()

if __name__ == '__main__':
    fetchdata()
    sys.exit()
