# cryCompare
Python wrapper for CryptoCompare public API (https://www.cryptocompare.com/api)

Following API requests are supported:
- CoinList
- Price
- PriceMulti
- PriceMultiFull
- PriceHistorical
- generateAvg
- dayAvg
- CoinSnapshot
- CoinSnapshotFullById
- HistoMinute
- HistoHour
- HistoDay
- topPairs
- socialStats
- miningEquipment

Wrapper requires following python modules:
- requests

Usage

```
from crycompare import price as p
print(p.coinSnapshot('btc', 'usd'))
```

price module: price, priceMulti, priceMultiFull, generateAvg, dayAvg, priceHistorical, coinSnapshot, coinSnahpshotFullById.
For detailed documentation visit CryptoCompare API website.

history module: histoMinute, histoHour, histoDay.
For detailed documentation visit CryptoCompare API website.

social module: socialStats, miningEquipment

CryptoCompare API Documentation can be found at https://www.cryptocompare.com/api/#introduction
