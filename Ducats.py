import requests
import json
import time
from datetime import date

def getAllItems():
    response = requests.get("https://api.warframe.market/v1/items")
    result = json.loads(response.text)
    ducats = {}

    for item in result["payload"]["items"]:
        url_name = item["url_name"]
        if isPrime(url_name) and item["url_name"] not in ducats:
            ducats.update(getItemData(url_name))
            time.sleep(0.5)

    return ducats


def getItemData(itemID: str):
    response = requests.get(f"https://api.warframe.market/v1/items/{itemID}")
    result = json.loads(response.text)
    ducats = {}

    for item in result["payload"]["item"]["items_in_set"]:
        if "ducats" in item:
            ducats[item["url_name"]] = {"ducats": item["ducats"], "name": item["en"]["item_name"]}

    return ducats


def isPrime(itemID: str):
    return "prime_" in itemID


def loadItems(f: str):
    with open(f, "r") as f:
        return json.load(f)


def saveItems(f: str):
    items = getAllItems()

    with open(f, "w") as f:
        json.dump(items, f)


def getItemPrices(f):
    items = loadItems(f)
    today = date.today()

    today = f"{today.year}-{today.month:02d}-{today.day - 1:02d}"
    response = requests.get(f"https://relics.run/history/price_history_{today}.json")
    result = json.loads(response.text)

    itemList = []

    for key, value in items.items():
        name = value["name"]
        avg_price = 1000
        ducats = value["ducats"]
        
        for trade in result[name]:
            if trade["order_type"] == "sell":
                avg_price = trade["avg_price"]

        ducats_per_plat = ducats / avg_price
        
        itemList.append((key, ducats_per_plat, ducats))
        itemList.sort(key=lambda x:x[1], reverse=True)

    return itemList


def getOptimalOrders(item, ducatsPerPlatCutoff):
    itemID, _, ducats = item

    orderDict = {}
    
    response = requests.get(f"https://api.warframe.market/v1/items/{itemID}/orders")
    result = json.loads(response.text)
    
    for order in result["payload"]["orders"]:
        if order["order_type"] == "sell":
            cost = order["platinum"]
            user = order["user"]["ingame_name"]
            
            if order["user"]["status"] == "ingame" and ducats / cost >= ducatsPerPlatCutoff:
                orderDict[user] = {"items": [],
                                    "platinum": 0,
                                    "ducats": 0}

                for _ in range(order["quantity"]):
                    orderDict[user]["ducats"] += ducats
                    orderDict[user]["platinum"] += cost
                    orderDict[user]["items"].append((itemID, ducats, cost))

    return orderDict
        

def getOptimalListings(items, ducatsPerPlatCutoff):
    items = list(filter(lambda x: x[1] > ducatsPerPlatCutoff / 2, items))
    orderDict = {}

    for item in items:
        newOrderDict = getOptimalOrders(item, ducatsPerPlatCutoff)
        orderDict = combineOrderDict(orderDict, newOrderDict)
        time.sleep(0.5)

    return orderDict


def combineOrderDict(one, two):
    for user in two:
        if user in one:
            one[user]["ducats"] += two[user]["ducats"]
            one[user]["platinum"] += two[user]["platinum"]
            one[user]["items"] += two[user]["items"]
            
        else:
            one[user] = two[user]
    
    return one


def filterListings(listings, minDucatsPerTrade=0, minDucatsPerPlat=0):
    minDucatsPerPlat = max(1, minDucatsPerPlat)
    listings = list(filter(lambda x: x[2] >= minDucatsPerTrade, listings))
    listings = list(filter(lambda x: x[2] / x[1] >= minDucatsPerPlat, listings))
    return listings


def listingsFromDict(listings):
    optimalListings = []
    for key, value in listings.items():
        optimalListings.append([key, value["platinum"], value["ducats"], value["items"]])
    
    return optimalListings


def findOptimalListings(listings, value=True):
    if value:
        listings.sort(key=lambda x:x[2] / x[1], reverse=True)
    else:
        listings.sort(key=lambda x:x[2], reverse=True)

    return listings


def buyOrders(listings, trades=1, minDucatsPerTrade=0, minDucatsPerPlat=0, value=True, finalListings=[]):
    listings = findOptimalListings(listings, value=value)
    listings = filterListings(listings, minDucatsPerTrade, minDucatsPerPlat)

    if trades == 0 or len(listings) == 0:
        return finalListings
    
    else:
        player = listings[0][0]
        items = listings[0][3]

        if value:
            items.sort(key=lambda x:x[2] / x[1], reverse=True)
        else:
            items.sort(key=lambda x:x[2], reverse=True)

        listings[0][3] = items[6:]
        for item in items:
            listings[0][1] -= item[1]
            listings[0][2] -= item[2]
        finalListings.append((player, items[0:6]))

        return buyOrders(listings, trades - 1, minDucatsPerTrade, value, finalListings=finalListings)
    

def printSales(listings, items):
    for sale in listings:
        print(f"{sale[0]}:")
        totalDucats = 0
        totalPrice = 0
        print()

        for item in sale[1]:
            itemName = items[item[0]]["name"]
            totalDucats += item[1]
            totalPrice += item[2]
            print(f"{itemName}: {item[1]} / {item[2]}")

        print()
        print(f"Total: {totalDucats} / {totalPrice}")
        print("\n")


def getIGNMessages(listings, items):
    messages = []

    for listing in listings:
        message = f"/w {listing[0]} Hi! I WTB "
        totalPrice = 0
        totalDucats = 0

        for item in listing[1]:
            totalDucats += item[1]
            totalPrice += item[2]
            itemName = items[item[0]]["name"]
            message += itemName + ", "

        message = message[:-2]
        message += f" for {totalPrice} platinum."

        messages.append((message, totalDucats, int(totalDucats / totalPrice)))

    return messages


def saveSales(fileName, listings, items):
    with open(fileName, "r") as f:
        sales = json.load(f)
    
    for listing in listings:
        for item in listing[1]:
            itemName = items[item[0]]["name"]
            ducats = item[1]
            price = item[2]

            if itemName in sales:
                sales[itemName]["quanity"] += 1
                sales[itemName]["price"] += price
            else:
                sales[itemName] = {}
                sales[itemName]["quanity"] = 1
                sales[itemName]["ducats"] = ducats
                sales[itemName]["price"] = price

            if "total" in sales:
                sales["total"]["price"] += price
                sales["total"]["ducats"] += ducats
            else:
                sales["total"] = {}
                sales["total"]["price"] = price
                sales["total"]["ducats"] = ducats

    with open(fileName, "w") as f:
        json.dump(sales, f)

if __name__ == "__main__":
    items = loadItems("items.json")
    prices = getItemPrices("items.json")
    listings = getOptimalListings(prices, 10)
    listings = listingsFromDict(listings)
    listings = buyOrders(listings, trades=20, minDucatsPerTrade=50, minDucatsPerPlat=15, value=True)
    messages = getIGNMessages(listings, items)
    
    with open("sales.txt", "w") as f:
        for message in messages:
            f.write(f"{message[1]} ({message[2]}): {message[0]}\n")
