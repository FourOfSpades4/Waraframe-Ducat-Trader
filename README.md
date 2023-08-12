# Waraframe-Ducat-Trader

This is a simple program to query warframe.market's API in order to determine
players who are selling large numbers of prime items with good ducat values.

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
