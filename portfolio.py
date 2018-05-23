from collections import OrderedDict
from coinmarketcap import Market


def get_holdings(client):
    return OrderedDict({
            coin["asset"]: float(coin["free"]) + float(coin["locked"])
            for coin in client.get_account()['balances']
            if float(coin["free"]) + float(coin["locked"]) > 0
    })


def get_prices(client, currency):
    prices = {currency: 1.0}
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
