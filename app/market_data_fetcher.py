import re
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from zoneinfo import ZoneInfo

class MarketDataFetcher:
    def __init__(self, exchange):
        try:
            self.exchange = exchange
        except Exception as e:
            st.error(f"An error occurred while initializing the MarketDataFetcher: {e}")

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int, selected_datetime: datetime,
                    local_tz: ZoneInfo, market_type: str) -> pd.DataFrame:
        try:
            if not hasattr(self.exchange, 'fetchOHLCV'):
                raise NotImplementedError(
                    f"The exchange '{self.exchange.id}' does not support OHLCV data fetching."
                )

            # Always use "before date" calculations
            delta = self.calculate_delta(timeframe, limit - 1)
            adjusted_date = selected_datetime - delta
            since = int(adjusted_date.timestamp() * 1000)

            fetchOHLCV_params = {}
            if self.exchange.id == "bybit" and market_type == "perpetual":
                fetchOHLCV_params = {'category': 'linear'}
            elif self.exchange.id == "bybit" and market_type == "spot":
                fetchOHLCV_params = {'category': 'spot'}

            all_data = []
            while limit > 0:
                batch_limit = min(limit, 500)  # Maximum number of candles per request
                data = self.exchange.fetchOHLCV(symbol, timeframe=timeframe, since=since, limit=batch_limit, params=fetchOHLCV_params)
                if not data:
                    break

                all_data.extend(data)
                limit -= len(data)
                since = data[-1][0] + 1  # Update 'since' to be the timestamp of the last candle + 1ms

            if all_data:
                df = pd.DataFrame(all_data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df['date'] = pd.to_datetime(df['date'], unit='ms', utc=True).dt.tz_convert(local_tz).dt.tz_localize(None)
                return df
            else:
                return pd.DataFrame()

        except ValueError as e:
            st.error(f"Value error: {e}")
            return pd.DataFrame()
        except NotImplementedError as e:
            st.error(f"Not implemented: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"An error occurred while fetching OHLCV data: {e}")
            return pd.DataFrame()

    def calculate_delta(self, timeframe: str, limit: int):
        try:
            match = re.fullmatch(r'(\d+)([mhdwM])', timeframe)
            if not match:
                raise ValueError(f"Invalid timeframe format: '{timeframe}'. Expected formats like '1m', '2h', '1M', etc.")

            amount_str, unit = match.groups()
            amount = int(amount_str)
            total_amount = amount * limit

            if unit == 'm':
                return timedelta(minutes=total_amount)
            elif unit == 'h':
                return timedelta(hours=total_amount)
            elif unit == 'd':
                return timedelta(days=total_amount)
            elif unit == 'w':
                return timedelta(weeks=total_amount)
            elif unit == 'M':
                return relativedelta(months=total_amount)
            else:
                raise ValueError(f"Unsupported timeframe unit: '{unit}'. Supported units are m, h, d, w, M.")
        except ValueError as e:
            st.error(f"An error occurred while calculating delta: {e}")
            return timedelta(0)
        except Exception as e:
            st.error(f"An error occurred during delta calculation: {e}")
            return timedelta(0)