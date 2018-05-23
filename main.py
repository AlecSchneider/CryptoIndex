import pprint
import time
from binance.client import Client
from index import calc_allocation, rebalance
from trading import buy, sell
from portfolio import get_market_caps, get_holdings, get_prices, calc_portfolio_value
from keys import api_key, api_secret
from index_config import default


def convert_to_seconds(s):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(s[:-1]) * seconds_per_unit[s[-1]]


def update_loop(config=default):
    currency = "BTC"
    non_trading = ["USDT"]
    start = None
    wait = convert_to_seconds(config["rebalance_rate"])
    while True:
        now = time.time()
        if start and now - start < wait:
            time.sleep(wait/10)
            continue

        client = Client(api_key, api_secret)

        caps = get_market_caps()
        holdings = get_holdings(client)
        prices = get_prices(client, currency)

        for coin in caps:
            if coin["symbol"] not in prices or coin["symbol"] in non_trading:
                caps.remove(coin)

        allocation = calc_allocation(caps, config)
        value = calc_portfolio_value(prices, holdings)

        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(allocation)

        trans = rebalance(prices, holdings, allocation, value)
        trans.sort(key=lambda tup: tup[1])

        for s, amount in trans:
            if s == currency:
                continue
            if amount > 0:
                order = buy(client, s+currency, amount)
                if order:
                    pp.pprint(order)
            if amount < 0:
                order = sell(client, s+currency, -amount)
                if order:
                    pp.pprint(order)
        print("Done rebalancing")

        start = time.time()


def main():
    update_loop()


if __name__ == "__main__":
    # execute only if run as a script
    main()
