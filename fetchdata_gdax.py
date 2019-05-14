import cbpro
import json
import sys
import os.path
homedir = os.path.expanduser("~")

def fetchdata():
    #reception des donnees orderbook gdax et stockage dans un fichier
    public_client = cbpro.PublicClient()
    with open(homedir +'/server_crypto/data_received_gdax.json', 'w') as f:
        data = public_client.get_product_order_book('BTC-EUR', level=2)
        data = json.dumps(data)
        f.write(data)

if __name__ == '__main__':
    fetchdata()
    sys.exit()
