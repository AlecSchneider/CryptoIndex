def calc_allocation(coins, config):
    top = config["top"]
    value = config["value"]
    max_percent = config["max_percent"]
    if top * max_percent < 1:
        raise ValueError('Not 100 percent', top, max_percent)

    for coin in coins:
        coin[value] = float(coin[value])
    coins = sorted(coins, key=lambda coin: coin[value], reverse=True)
    coins = coins[:top]

    values_sum = sum([coin[value] for coin in coins])
    allocation = {}
    left = 1
    while left * coins[0][value] / values_sum > max_percent:
        allocation[coins[0]["symbol"]] = max_percent
        values_sum -= coins[0][value]
        left -= max_percent
        coins = coins[1:]

    allocation.update({
        coin["symbol"]: left * coin[value] / values_sum
        for coin in coins
        })
    return allocation


def rebalance(prices, holdings, allocation):
    holdings.update({symbol: 0 for symbol in allocation.keys() - holdings.keys()})
    allocation.update({symbol: 0 for symbol in holdings.keys() - allocation.keys()})
    holdings_value = {
            symbol: prices[symbol] * amount
            for symbol, amount in holdings.items()
            }
    holdings_value_sum = sum(holdings_value.values())
    transactions = []
    for symbol, amount in holdings_value.items():
        change = allocation[symbol] * holdings_value_sum - amount
        if change != 0:
            transactions.append((symbol, change))
    return transactions
