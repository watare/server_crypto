const Gdax = require('coinbase-pro');
var fs = require('fs');
var sleep = require('sleep');
var date = (Date.now()-Date.now()%1000)/1000

var orderbookSync = new Gdax.OrderbookSync('BTC-EUR');

orderbookSync.on('message',data => {
  var book = orderbookSync.books['BTC-EUR'].state();
  if(book.bids.length == 0 && book.asks.length == 0){
    //console.log("Waiting for data...");
  }
  else {
    var date2 = (Date.now()-Date.now()%1000)/1000
    if ((date2-date)/60 >1.0) {
      date = (Date.now()-Date.now()%1000)/1000;
      date_fichier = date -date%60
      donnees = JSON.stringify(book);
      fs.writeFile('orderbook_data/'+date_fichier+'.json',donnees, 'utf8', function(err) {
        if (err) throw err;
          console.log('erreur');
        });
    }else{
      console.log('pas de ecriture');
    }

// regarder comment faire un update uniquement de maniere periodique time sleep
    //console.log(JSON.stringify(book));
  }
});
