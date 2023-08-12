# Waraframe-Ducat-Trader

This is a simple program to query warframe.market's API in order to determine
players who are selling large numbers of prime items with good ducat values.

It will first filter all the items being sold on warframe.market in the past in order
to determine which items have a chance at being sold for a good ducat per price threshold. 

Then, it will get all the listings for those items, determine which players are selling the most 
of those items, and give ingame whispers requesting to purchase those items, along with the 
total price, ducats, and ducats per plat from that trade.

<br/>

## How To Use

If you'd like, just run the current code. You can edit the bottom lines to change
paramters.

To create a file containing all prime items and their ducat costs, run 
`saveItems(ITEMS_FILE_NAME)`

To load a file containing all prime items and their ducat costs, run 
`items = loadItems(ITEMS_FILE_NAME)`

To load all current item pricings from history (using relics.run's API) run 
`prices = getItemPrices(ITEMS_FILE_NAME)`

To get all Optimal Listings above a certain minDucatsPerPlat threshold, run 
`listings = getOptimalListings(prices, threshold)`

To get a list of buy orders above a certain ducat threshold, run
```
listings = listingsFromDict(listings)
listings = buyOrders(listings, trades=, minDucatsPerTrade=, minDucatsPerPlat=, value=)
  - trades:            Upper limit of trades to make. Defaults to 1
  - minDucatsPerTrade: Minimum ducats accepted per trade
  - minDucatsPerPlat:  Minimum ducats accepted per plat
  - value:             Whether to filter by max ducats per plat or max ducats
```

To get a list of messages to send to these players, run 
```
messages = getIGNMessages(listings, items)
  - This returns a list of of message to send in the form: ((message), (ducats), (ducats per plat))
```

Full Example:
```
items = loadItems("items.json")
prices = getItemPrices("items.json")
listings = getOptimalListings(prices, 10)
listings = listingsFromDict(listings)
listings = buyOrders(listings, trades=10, minDucatsPerTrade=50, minDucatsPerPlat=15, value=True)
messages = getIGNMessages(listings, items)
```

### Disclaimer

This is not meant to be a professional piece of software, or even remotely close. 
It was made as a fun mini-project to make me a little bit of plat, and has many flaws, 
especially with how I implemented it. I don't use it often enough to re-rewrite it in order
to give it a GUI or make the code actually good, so I'm just going to make it public for anyone to 
use, or ideally improve if they'd like.
