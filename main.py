import pprint
from binance.client import Client
from coinmarketcap import Market
from index import calc_allocation

from index_config import market_cap_20
from keys import api_key, api_secret

# client = Client(api_key, api_secret)

# # get all symbol prices
# prices = client.get_all_tickers()

# coinmarketcap = Market()
# coins = coinmarketcap.ticker()
pp = pprint.PrettyPrinter(indent=4)
allocation = calc_allocation(market_cap_20)
pp.pprint(allocation)
print(sum(allocation.values()))


