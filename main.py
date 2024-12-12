from config import SUPPORTED_EXCHANGES
from app.timeframe_delta_calculator import TimeframeDeltaCalculator
from app.market_data_fetcher import MarketDataFetcher
from app.data_saver import CsvSaver
from app.indicators import IndicatorRegistry, EmaIndicator, MacdIndicator
from app.crypto_data_facade import CryptoDataFacade
from app.chart_renderer import ChartRenderer
from app.crypto_data_app import CryptoDataApp

def main():
    # Setup dependencies
    exchange_name = "bybit"  # Default, can be changed if needed
    exchange = SUPPORTED_EXCHANGES[exchange_name]

    delta_calculator = TimeframeDeltaCalculator()
    fetcher = MarketDataFetcher(exchange, delta_calculator)

    # Setup indicators
    indicator_registry = IndicatorRegistry()
    indicator_registry.register('ema_10', EmaIndicator(10))
    indicator_registry.register('ema_20', EmaIndicator(20))
    indicator_registry.register('macd', MacdIndicator())

    facade = CryptoDataFacade(fetcher, indicator_registry)
    chart_renderer = ChartRenderer()
    saver = CsvSaver()

    app = CryptoDataApp(facade, chart_renderer, saver)
    app.display()

if __name__ == "__main__":
    main()
