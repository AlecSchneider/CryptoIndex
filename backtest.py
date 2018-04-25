import matplotlib.pyplot as plt
import datetime as dt
from cryptohist.coinmarketcap import CoinMarketCapFetcher

def get_historical_data(start=dt.datetime(2013, 4, 28), end=dt.datetime.today()):
    # Import Bitcoin historical data
    price = 'Open'
    value = 'Market Cap'
    fetcher = CoinMarketCapFetcher(start=start, end=end)
    symbols = fetcher.get_symbols()[1:20]
    df = fetcher.fetch_by_symbol('BTC')
    df['BTC'] = df[price]
    prices = df[['BTC']]
    df['BTC'] = df[value]
    caps = df[['BTC']]

    for symbol in symbols:
        print(symbol)
        df = fetcher.fetch_by_symbol(symbol)
        df[symbol] = df[price]
        prices = prices.join(df[[symbol]])
        df[symbol] = df[value]
        caps = caps.join(df[[symbol]])

    return prices, caps

def backtest_index(config):
    prices, caps = get_historical_data(start=dt.datetime(2018, 1, 1))

backtest_index()
