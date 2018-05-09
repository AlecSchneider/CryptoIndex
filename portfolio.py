from binance.client import Client
from keys import api_key, api_secret
from main import get_holdings, get_prices, calc_portfolio_value


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

