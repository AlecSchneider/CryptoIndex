import pprint
from binance.client import Client
from index import calc_allocation, rebalance
from trading import buy, sell
from portfolio import get_market_caps, get_holdings, get_prices, calc_portfolio_value
from keys import api_key, api_secret
from index_config import market_cap_20


def main():
    currency = "BTC"
    non_trading = ["USDT"]
    client = Client(api_key, api_secret)

    caps = get_market_caps()
    holdings = get_holdings(client)
    prices = get_prices(client, currency)

    for coin in caps:
        if coin["symbol"] not in prices or coin["symbol"] in non_trading:
            caps.remove(coin)

    allocation = calc_allocation(caps, market_cap_20)
    value = calc_portfolio_value(prices, holdings)

    # Pretty print some of this
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(holdings)
    pp.pprint(prices)
    pp.pprint(caps[:20])
    pp.pprint(allocation)
    print(value)

    trans = rebalance(prices, holdings, allocation, value)
    trans.sort(key=lambda tup: tup[1])
    pp.pprint(trans)

    ans = input("Are you sure you wanna do that? Y/n: ")
    if ans != 'Y':
        print("No transactions have been executed")
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
