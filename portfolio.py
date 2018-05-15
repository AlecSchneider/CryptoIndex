from binance.client import Client
from coinmarketcap import Market
from keys import api_key, api_secret


def get_holdings(client):
    return {
            coin["asset"]: float(coin["free"]) + float(coin["locked"])
            for coin in client.get_account()['balances']
            if float(coin["free"]) + float(coin["locked"]) > 0
    }


def get_prices(client, currency):
    prices = {currency: 1}
    for coin in client.get_all_tickers():
        if currency not in coin["symbol"]:
            continue
        symbol = coin["symbol"].replace(currency, "")
        prices[symbol] = float(coin["price"])
    return prices


def get_market_caps(top=100):
    coinmarketcap = Market()
    caps = [
            {"symbol": coin["symbol"], "value": coin["market_cap_usd"]}
            for coin in coinmarketcap.ticker(start=0, limit=top)
            ]
    return caps


def calc_portfolio_value(prices, holdings):
    return sum([
        amount * prices[symbol]
        if symbol in prices else amount
        for symbol, amount in holdings.items()
    ])


def calc_allocation(value, prices, holdings):
    return [
            (symbol, round(prices[symbol] * amount / value * 100, 2))
            for symbol, amount in holdings.items()
            ]


def print_portfolio(allocation):
    for s, a in sorted(allocation, key=lambda tup: tup[1], reverse=True):
        print(s, ":", a, "%")


currency = "BTC"
client = Client(api_key, api_secret)
holdings = get_holdings(client)
prices = get_prices(client, currency)
value = calc_portfolio_value(prices, holdings)
allocation = calc_allocation(value, prices, holdings)

print(value * prices["USDT"], "$")
print_portfolio(allocation)
