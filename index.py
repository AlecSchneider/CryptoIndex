from coinmarketcap import Market


def calc_allocation(config):
    top = config["top"]
    value = config["value"]
    max_percent = config["max_percent"]/100
    if top * max_percent < 1:
        raise ValueError('Not 100 percent', top, max_percent)

    coinmarketcap = Market()
    coins = coinmarketcap.ticker(end=0)
    for coin in coins:
        coin[value] = float(coin[value])
    coins = sorted(coins, key=lambda coin: coin[value], reverse=True)
    coins = coins[:top]

    values_sum = sum([coin[value] for coin in coins])
    allocation = {}
    left = 1
    while left*coins[0][value]/values_sum > max_percent:
        allocation[coins[0]["symbol"]] = max_percent
        values_sum -= coins[0][value]
        left -= max_percent
        coins = coins[1:]

    allocation.update({coin["symbol"]: left*coin[value]/values_sum for coin in coins})
    return allocation


def rebalance(old_allocation, new_allocation):
    transactions = []
    return transactions
