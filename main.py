import pprint
from coinmarketcap import Market
from collections import OrderedDict
from binance.client import Client
from index import calc_allocation, rebalance

from index_config import market_cap_20
from keys import api_key, api_secret


def sell(client, symbol, amount):
    filters = client.get_symbol_info(symbol)["filters"]
    lot_size = get_lot_size(filters)
    round_num = get_rounding_num(float(lot_size["stepSize"]))
    q = round(amount, round_num)
    if q > amount:
        q -= float(lot_size["stepSize"])
    if q < float(lot_size["minQty"]):
        return

    return client.create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=q)


def buy(client, symbol, amount):
    filters = client.get_symbol_info(symbol)["filters"]
    lot_size = get_lot_size(filters)
    round_num = get_rounding_num(float(lot_size["stepSize"]))
    q = round(amount, round_num)
    if q < float(lot_size["minQty"]):
        return

    return client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=q)


def get_rounding_num(n):
    i = 0
    while n < 1:
        n *= 10
        i += 1

    return i


def get_lot_size(filters):
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            return f


def main():
    currency = "BTC"
    non_trading = [currency, "USDT"]
    client = Client(api_key, api_secret)
    coinmarketcap = Market()
    caps = [
            {"symbol": coin["symbol"], "value": coin["market_cap_usd"]}
            for coin in coinmarketcap.ticker(start=0, limit=100)
            ]

    pp = pprint.PrettyPrinter(indent=4)
    holdings = {
            coin["asset"]: float(coin["free"]) + float(coin["locked"])
            for coin in client.get_account()['balances']
            if float(coin["free"]) + float(coin["locked"]) > 0
            }
    prices = {currency: 1}
    for coin in client.get_all_tickers():
        if currency not in coin["symbol"]:
            continue
        symbol = coin["symbol"].replace(currency, "")
        prices[symbol] = float(coin["price"])

    for coin in caps:
        if coin["symbol"] not in prices or coin["symbol"] in non_trading:
            caps.remove(coin)


    pp.pprint(holdings)
    pp.pprint(prices)
    pp.pprint(caps[:20])
    allocation = calc_allocation(caps, market_cap_20)
    pp.pprint(allocation)
    value = sum([
        amount * prices[symbol]
        if symbol in prices else amount
        for symbol, amount in holdings.items()
        ])
    print(value)
    trans = rebalance(prices, holdings, allocation, value * 0.95)
    trans.sort(key=lambda tup: tup[1])
    pp.pprint(trans)
    ans = input("Are you sure you wanna do that? Y/n: ")
    if ans != 'Y':
        return

    for s, amount in trans:
        if s == currency:
            continue
        if amount > 0:
            order = buy(client, s+currency, amount)
            print(order)
        if amount < 0:
            order = sell(client, s+currency, -amount)
            print(order)



if __name__ == "__main__":
    # execute only if run as a script
    main()
