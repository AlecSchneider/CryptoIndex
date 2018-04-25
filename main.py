import pprint
from binance.client import Client
from coinmarketcap import Market
from index import calc_allocation, rebalance

from index_config import market_cap_20
from keys import api_key, api_secret

# client = Client(api_key, api_secret)

# # get all symbol prices
# prices = client.get_all_tickers()

capital_usd = 500

coinmarketcap = Market()
coins = coinmarketcap.ticker()
prices_usd = {coin["symbol"]: float(coin["price_usd"]) for coin in coins}
capital_btc = capital_usd / prices_usd["BTC"]

pp = pprint.PrettyPrinter(indent=4)
allocation = calc_allocation(coins, market_cap_20)
pp.pprint(allocation)
transactions = rebalance(prices_usd, {'BTC': capital_btc}, allocation)
pp.pprint(transactions)
