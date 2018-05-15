from binance.client import Client


def sell(client, symbol, amount):
    filters = client.get_symbol_info(symbol)["filters"]
    lot_size = get_lot_size(filters)
    round_num = get_rounding_num(float(lot_size["stepSize"]))
    q = round(amount, round_num)
    if q > amount:
        q -= float(lot_size["stepSize"])
    if q < float(lot_size["minQty"]):
        return

    return client.create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=q)


def buy(client, symbol, amount):
    filters = client.get_symbol_info(symbol)["filters"]
    lot_size = get_lot_size(filters)
    round_num = get_rounding_num(float(lot_size["stepSize"]))
    q = round(amount, round_num)
    if q < float(lot_size["minQty"]):
        return

    return client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=q)


def get_rounding_num(n):
    i = 0
    while n < 1:
        n *= 10
        i += 1

    return i


def get_lot_size(filters):
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            return f
