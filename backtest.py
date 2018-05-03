import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
from coinmarketcap import CoinMarketCapFetcher
from index import calc_allocation, rebalance
from index_config import market_cap_20, market_cap_50, market_cap_10, market_cap_10_no_limit


def get_historical_data(start=dt.datetime(2013, 4, 28), end=dt.datetime.today()):
    # Import Bitcoin historical data
    price = 'Open'
    value = 'Market Cap'
    fetcher = CoinMarketCapFetcher(start=start, end=end)
    symbols = fetcher.get_symbols()[1:200]
    df = fetcher.fetch_by_symbol('BTC')
    df['BTC'] = df[price]
    prices = df[['BTC']]
    df['BTC'] = df[value]
    caps = df[['BTC']]

    for symbol in symbols:
        df = fetcher.fetch_by_symbol(symbol)
        df[symbol] = df[price]
        prices = prices.join(df[[symbol]])
        df[symbol] = df[value]
        caps = caps.join(df[[symbol]])

    return prices, caps

def backtest_index(configs=[], start=dt.datetime(2018, 2, 15)):
    prices, caps = get_historical_data(start=start)
    strategies = pd.DataFrame()

    hodl = ["BTC", "ETH"]
    # Hodling
    for coin in hodl:
        initial_price = prices[coin][0]
        strategies[coin] = prices[coin]
        strategies[coin] = strategies[coin].map(lambda x: x / initial_price)

    coins = []
    for index, row in caps.iterrows():
        coins.append([{"symbol": col, "market_cap_usd": row[col]} for col in caps if row[col] > 0])
    for config in configs:
        allocations = [calc_allocation(coin, config) for coin in coins]
        holdings = [{"USD": 1}]
        prices["USD"] = 1
        p = []
        j = 0
        for index, row in prices.iterrows():
            n = {}
            for col in prices:
                if max(0, float(row[col])) > 0:
                    n[col] = row[col]
                elif j > 0:
                    n[col] = prices[col][j-1]
                else:
                    n[col] = 0
            j += 1
            p.append(n)

        for i, allocation in enumerate(allocations):
            if i % int(365/24) == 0:
                holdings.append(rebalance(p[i], holdings[-1], allocation))
            else:
                holdings.append(holdings[-1])
        holdings = holdings[1:]
        initial_price = 0.0
        strategies[config["name"]] = 0.0
        for coin, amount in holdings[0].items():
            if amount > 0:
                initial_price += p[0][coin] * amount
        for i, holding in enumerate(holdings):
            for coin, amount in holding.items():
                if amount > 0:
                    strategies[config["name"]][i] += p[i][coin] * amount
        strategies[config["name"]] = strategies[config["name"]].map(lambda x: x / initial_price)

    plot = strategies.plot()
    plot.axhline(y=1, color="red")
    plt.show()

backtest_index(configs=[market_cap_20, market_cap_50, market_cap_10, market_cap_10_no_limit])
