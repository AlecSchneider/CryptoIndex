from cryptohist import CoinMarketCapFetcher
import datetime as dt

fetcher = CoinMarketCapFetcher(start=dt.datetime(2013, 4, 28), end=dt.datetime.today())
symbols = set(fetcher.get_symbols())
for symbol in symbols:
    print(symbol)
    df = fetcher.fetch_by_symbol(symbol)
    df.to_csv("data/" + symbol + ".csv")
