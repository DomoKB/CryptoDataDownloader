from app.market_data_fetcher import MarketDataFetcher
from app.indicators import IndicatorRegistry
from app.data_saver import DataSaverStrategy
import streamlit as st
import pandas as pd

class CryptoDataFacade:
    def __init__(self, fetcher: MarketDataFetcher, indicator_registry: IndicatorRegistry):
        self.fetcher = fetcher
        self.indicator_registry = indicator_registry

    def fetch_data(self, symbol: str, timeframe: str, limit: int, selected_datetime, local_tz, market_type: str):
        try:
            return self.fetcher.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
                selected_datetime=selected_datetime,
                local_tz=local_tz,
                market_type=market_type
            )
        except Exception as e:
            st.error(f"An error occurred while fetching OHLCV data: {e}")

    def calculate_indicator(self, indicator_name: str, data: pd.DataFrame) -> pd.DataFrame:
        try:
            if data.empty:
                return pd.DataFrame()
            indicator = self.indicator_registry.get(indicator_name)
            return indicator.calculate(data)
        except Exception as e:
            st.error(f"An error occurred while calculating the {indicator_name} indicator: {e}")
            return pd.DataFrame()

    def save_data(self, data: pd.DataFrame, saver_strategy: DataSaverStrategy, filename: str):
        try:
            saver_strategy.save(data, filename)
        except Exception as e:
            st.error(f"An error occurred while saving data: {e}")