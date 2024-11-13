from app.market_data_fetcher import MarketDataFetcher
from app.indicator_calculator import IndicatorCalculator
import streamlit as st
import pandas as pd

class CryptoDataFacade:
    def __init__(self, exchange):
        try:
            self.exchange = exchange
            self.fetcher = MarketDataFetcher(self.exchange)
        except Exception as e:
            st.error(f"An error occurred while initializing the CryptoDataFacade: {e}")

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

    def calculate_indicator(self, indicator_name: str, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        # Calculate indicators based on hardcoded allowed indicators
        try:
            if data.empty:
                return pd.DataFrame()
            if indicator_name == 'ema':
                return IndicatorCalculator.calculate_ema(data, kwargs.get('length', 10))
            elif indicator_name == 'macd':
                return IndicatorCalculator.calculate_macd(
                    data, kwargs.get('fast', 12), kwargs.get('slow', 26), kwargs.get('signal', 9)
                )
            else:
                raise ValueError(f"Indicator '{indicator_name}' is not supported.")
        except Exception as e:
            st.error(f"An error occurred while calculating the {indicator_name} indicator: {e}")

    def save_data(self, data: pd.DataFrame, saver_strategy, filename: str):
        try:
            saver_strategy.save(data, filename)
        except Exception as e:
            st.error(f"An error occurred while saving data: {e}")
