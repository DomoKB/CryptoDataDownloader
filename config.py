import ccxt

SUPPORTED_EXCHANGES = {
    "binance": ccxt.binance(),
    "bybit": ccxt.bybit()
}

SUPPORTED_TIMEFRAMES = {
    "binance": [
        "1m", "3m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "8h",
        "12h", "1d", "3d", "1w", "1M"
    ],
    "bybit": [
        "1m", "3m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "12h",
        "1d", "1w", "1M"
    ]
}

EXTRA_CANDLES = 100
SAVE_DIRECTORY = 'saved_data'
DEFAULT_TRADING_PAIR = 'BTCUSDT'
DEFAULT_EXCHANGE = 'bybit'
DEFAULT_MARKET_TYPE = 'perpetual'  # or 'spot' based on exchange
