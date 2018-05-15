import index
import unittest

coins = [
        {"symbol": "BTC", "price_usd": "100", "market_cap": "1000"},
        {"symbol": "ETH", "price_usd": "50", "market_cap": "500"},
        {"symbol": "RPL", "price_usd": "25", "market_cap": "50"},
        ]
holdings = {"BTC": 1, "ETH": 4}
allocation = {"BTC": 2/3, "ETH": 1/3}
config = {"top": 2, "value": "market_cap", "max_percent": 100}


class TestIndex(unittest.TestCase):
    def test_calc_allocations(self):
        a = index.calc_allocation(coins, config)
        self.assertEqual(a, allocation)

    def test_rebalance(self):
        prices_usd = {coin["symbol"]: float(coin["price_usd"]) for coin in coins}
        prices_usd["USD"] = 1
        t1 = index.rebalance(prices_usd, {"USD": 600}, allocation)
        self.assertAlmostEqual(t1, [('USD', -600.0), ('BTC', 400.0), ('ETH', 200.0)])

        t2 = index.rebalance(prices_usd, holdings, allocation)
        self.assertEqual(t2, [('BTC', 100.0), ('ETH', -100.0)])


if __name__ == '__main__':
    unittest.main()
