import pickle
import pprint
from binance.client import Client
from collections import OrderedDict
from coinmarketcap import Market
from keys import api_key, api_secret
from cryptohist import CoinMarketCapFetcher
from datetime import datetime, timezone, timedelta, date
import pandas as pd
from cryCompare.crycompare import history as h
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import style


def get_holdings(client):
    return OrderedDict({
            coin["asset"]: float(coin["free"]) + float(coin["locked"])
            for coin in client.get_account()['balances']
            if float(coin["free"]) + float(coin["locked"]) > 0
    })


def get_prices(client, currency):
    prices = {currency: 1.0}
    for coin in client.get_all_tickers():
        if currency not in coin["symbol"]:
            continue
        symbol = coin["symbol"].replace(currency, "")
        prices[symbol] = float(coin["price"])
    return prices


def get_market_caps(top=100):
    coinmarketcap = Market()
    caps = [
            {"symbol": coin["symbol"], "value": coin["market_cap_usd"]}
            for coin in coinmarketcap.ticker(start=0, limit=top)
            ]
    return caps


def calc_portfolio_value(prices, holdings):
    return sum([
        amount * prices[symbol]
        if symbol in prices else amount
        for symbol, amount in holdings.items()
    ])


def calc_allocation(value, prices, holdings):
    return [
            (symbol, round(prices[symbol] * amount / value * 100, 2))
            for symbol, amount in holdings.items()
            ]


def print_portfolio(allocation):
    for s, a in sorted(allocation, key=lambda tup: tup[1], reverse=True):
        print(s, ":", a, "%")


def get_performance(client, start=datetime(2018, 2, 5), end=datetime.today()):
    to_ts = int(end.replace(tzinfo=timezone.utc).timestamp())
    limit = (end-start).days
    currency = 'BTC'

    holdings = get_holdings(client)
    trades = get_all_trades(client)
    coin_movements = get_coin_movements(trades)
    account_movements = get_account_movements(client)
    capital_df = get_capital_df(list(account_movements), start, end)
    df_holdings = get_holdings_df(holdings, coin_movements + account_movements, start, end)

    historical_prices = OrderedDict()
    for symbol in df_holdings.keys():
        if symbol == currency:
            continue
        data = h.histo_day(symbol, currency, e='Binance', to_ts=to_ts, limit=limit)
        historical_prices[symbol] = get_price_df(data)

    prices_df = pd.DataFrame(historical_prices, columns=historical_prices.keys())
    prices_df[currency] = 1.0

    df_currency_price = get_price_df(h.histo_day(currency, 'USDT', e='Binance', to_ts=to_ts, limit=limit))
    prices_df = prices_df.reindex_axis(sorted(prices_df.columns), axis=1)
    df_holdings = df_holdings.reindex_axis(
            sorted(df_holdings.columns), axis=1
            )
    print(df_holdings.head())
    holdings_values_df = pd.DataFrame(
                df_holdings.values*prices_df.values,
                columns=df_holdings.columns,
                index=df_holdings.index
                ).sum(1)

    style.use("ggplot")
    holdings_values_df.pct_change().fillna(0).add(1).cumprod().sub(1).plot(label='portfolio')
    df_currency_price.pct_change().fillna(0).add(1).cumprod().sub(1).plot(label='BTC')
    plt.legend(loc=2)
    plt.show()


def get_account_movements(client):
    deposits = client.get_deposit_history()
    withdraws = client.get_withdraw_history()
    deposits = [
            {
                "date": datetime.fromtimestamp(int(d['insertTime'])/1000),
                "symbol": d["asset"],
                "amount": d["amount"],
            }
            for d in deposits["depositList"]
            ]
    withdraws = [
            {
                "date": datetime.fromtimestamp(int(w['applyTime'])/1000),
                "symbol": w["asset"],
                "amount": -w["amount"],
            }
            for w in withdraws["withdrawList"]
            ]
    return sorted(deposits + withdraws, key=lambda k: k['date'])


def get_all_trades(client):
    trades = []
    try:
        with open('trades.pkl', 'rb') as f:
            trades = pickle.load(f)
    except (OSError, IOError) as e:
        tickers = client.get_all_tickers()
        for ticker in tickers:
            trades += [
                    (ticker['symbol'], trade)
                    for trade in client.get_my_trades(symbol=ticker['symbol'])
                    ]
        with open('trades.pkl', 'wb') as f:
            pickle.dump(trades, f)
    return trades


def get_coin_movements(trades):
    markets_binance = ["BNB", "USDT", "BTC", "ETH"]
    coin_movements = []
    for symbol, trade in trades:
        s1, s2 = "", ""
        for s in markets_binance:
            if s == symbol[-3:]:
                s2 = symbol[-3:]
                s1 = symbol[:-3]
            elif s == symbol[-4:]:
                s2 = symbol[-4:]
                s1 = symbol[:-4]

        buy = 1
        if not trade['isBuyer']:
            buy = -1

        coin_movements.append({
            "date": datetime.fromtimestamp(int(trade['time'])/1000),
            "symbol": s2,
            "amount": -buy * float(trade['qty']) * float(trade['price']),
            })
        coin_movements.append({
            "date": datetime.fromtimestamp(int(trade['time'])/1000),
            "symbol": s1,
            "amount": buy * float(trade['qty']),
            })
        coin_movements.append({
            "date": datetime.fromtimestamp(int(trade['time'])/1000),
            "symbol": trade['commissionAsset'],
            "amount": -float(trade['commission']),
            })

    return sorted(coin_movements, key=lambda k: k['date'])


def get_holdings_df(holdings, coin_movements, start, end):
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    coin_movements.sort(key=lambda k: k['date'])
    df = pd.DataFrame(columns=["date"] + list(holdings.keys()))
    i = 0
    while today >= start:
        if i == 0:
            df.loc[i] = [today] + list(holdings.values())
        else:
            df.loc[i] = df.loc[i-1]
            df.loc[i, "date"] = today
        while len(coin_movements) > 0 and coin_movements[-1]["date"] >= today:
            t = coin_movements.pop()
            s, a = t["symbol"], t["amount"]
            if s not in df.columns:
                df[s] = 0
            df.loc[i, s] -= a
        today -= timedelta(days=1)
        i += 1
    df.index = df["date"]
    del df["date"]
    return df.iloc[::-1]


def get_capital_df(account_movements, start, end):
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    capital = OrderedDict()
    for m in account_movements:
        try:
            capital[m["symbol"]] += m["amount"]
        except KeyError:
            capital[m["symbol"]] = m["amount"]
    df = pd.DataFrame(columns=["date"] + list(capital.keys()))
    i = 0
    while today >= start:
        if i == 0:
            df.loc[i] = [today] + list(capital.values())
        else:
            df.loc[i] = df.loc[i-1]
            df.loc[i, "date"] = today
        while len(account_movements) > 0 and account_movements[-1]["date"] >= today:
            t = account_movements.pop()
            s, a = t["symbol"], t["amount"]
            if s not in df.columns:
                df[s] = 0
            df.loc[i, s] -= a
        today -= timedelta(days=1)
        i += 1
    df.index = df["date"]
    del df["date"]
    return df.iloc[::-1]


def get_price_df(data):
    df_data = pd.DataFrame(data)
    df_data["date"] = df_data["time"].apply(datetime.utcfromtimestamp)
    df_data.index = df_data['date']
    df_data["price"] = (df_data["high"] + df_data["low"]) / 2
    return df_data["price"]


def main():
    currency = "BTC"
    client = Client(api_key, api_secret)
    holdings = get_holdings(client)
    prices = get_prices(client, currency)
    value = calc_portfolio_value(prices, holdings)
    allocation = calc_allocation(value, prices, holdings)

    print(value * prices["USDT"], "$")
    print_portfolio(allocation)
    print(get_performance(client))


if __name__ == "__main__":
    # execute only if run as a script
    main()
