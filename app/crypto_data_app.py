import streamlit as st
import os
import ccxt
from config import SUPPORTED_EXCHANGES, SUPPORTED_TIMEFRAMES, EXTRA_CANDLES
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, available_timezones
from app.crypto_data_facade import CryptoDataFacade
from app.chart_renderer import ChartRenderer
from app.data_saver import DataSaverStrategy

class CryptoDataApp:
    def __init__(self, facade: CryptoDataFacade, chart_renderer: ChartRenderer, saver: DataSaverStrategy):
        self.facade = facade
        self.chart_renderer = chart_renderer
        self.saver = saver
        self.exchange_name = None
        self.symbol = None
        self.market_type = None
        self.timeframe = None
        self.limit = None
        self.selected_date = None
        self.selected_time = None
        self.local_tz = None
        if 'data' not in st.session_state:
            st.session_state['data'] = None
        if 'trading_pair_input' not in st.session_state:
            st.session_state['trading_pair_input'] = 'BTCUSDT'  # Initialize with default value

    def display(self):
        try:
            st.set_page_config(layout="wide")
            st.subheader("Crypto Data Downloader")

            self.setup_sidebar()
            
            if st.session_state['data'] is not None:
                self.chart_renderer.display_chart(st.session_state['data'], self.symbol)
                self.setup_save_data()
                
        except Exception as e:
            st.error(f"An error occurred in the display method: {e}")

    def setup_sidebar(self):
        with st.sidebar:
            try:
                self.select_exchange()
                self.setup_market_type()
                self.select_timeframe()
                self.setup_datetime_inputs()

                if st.button("Fetch Data"):
                    self.fetch_and_display_data()

            except Exception as e:
                st.error(f"An error occurred in the input setup: {e}")

    def select_exchange(self):
        self.exchange_name = st.selectbox("Select Exchange", list(SUPPORTED_EXCHANGES.keys()), index=1)  # Default to bybit

        # Auto-capitalize the trading pair input
        def capitalize_symbol():
            st.session_state.trading_pair_input = st.session_state.trading_pair_input.upper()

        st.text_input(
            "Enter Trading Pair (e.g., BTCUSDT, ETHUSDT)",
            key="trading_pair_input",
            on_change=capitalize_symbol
        )

        self.symbol = st.session_state.trading_pair_input.upper()

    def setup_market_type(self):
        if self.exchange_name == "bybit":
            self.market_type = st.selectbox("Select Market Type", ["spot", "perpetual"], index=1)
        else:
            self.market_type = "spot"

    def select_timeframe(self):
        try:
            timeframes = SUPPORTED_TIMEFRAMES[self.exchange_name]
            default_timeframe = "4h" if "4h" in timeframes else timeframes[0]
            default_index = timeframes.index(default_timeframe)
            
            self.timeframe = st.selectbox("Select Timeframe", timeframes, index=default_index)
            self.limit = st.number_input("Number of Candles", min_value=10, max_value=1000, value=60, step=1)
        except KeyError:
            st.error(f"Timeframes not defined for exchange: {self.exchange_name}")
        except Exception as e:
            st.error(f"An error occurred while selecting timeframe: {e}")

    def setup_datetime_inputs(self):
        timezones_with_offsets = self.get_timezones_with_offsets()
        default_timezone_index = next((i for i, tz in enumerate(timezones_with_offsets) if "Australia/Sydney" in tz), 0)
        selected_timezone = st.selectbox("Select Timezone", timezones_with_offsets, index=default_timezone_index)
        self.local_tz = ZoneInfo(selected_timezone.split(" ")[0])
        self.selected_date = st.date_input("Select Date")
        self.selected_time = st.time_input("Select Time")

    def get_timezones_with_offsets(self):
        try:
            timezones = sorted(available_timezones())
            timezone_offset_list = []
            for tz_name in timezones:
                tz = ZoneInfo(tz_name)
                now = datetime.now(tz)
                offset = now.utcoffset()
                if offset is not None:
                    hours_offset = int(offset.total_seconds() / 3600)
                    minutes_offset = int((offset.total_seconds() % 3600) / 60)
                    formatted_offset = f"UTC{hours_offset:+03d}:{minutes_offset:02d}"
                    timezone_offset_list.append(f"{tz_name} ({formatted_offset})")
            return timezone_offset_list
        except Exception as e:
            st.error(f"An error occurred while fetching timezones: {e}")
            return []

    def fetch_and_display_data(self):
        try:
            data = self.facade.fetch_data(
                symbol=self.symbol, 
                timeframe=self.timeframe, 
                limit=self.limit + EXTRA_CANDLES,
                selected_datetime=self.get_selected_datetime(),
                local_tz=self.local_tz, 
                market_type=self.market_type
            )
            if data is not None and not data.empty:
                ema_10_df = self.facade.calculate_indicator('ema_10', data)
                ema_20_df = self.facade.calculate_indicator('ema_20', data)
                macd_df = self.facade.calculate_indicator('macd', data)
                
                trimmed_data = self.trim_data(data, ema_10_df, ema_20_df, macd_df)
                st.session_state['data'] = trimmed_data
            else:
                st.error("No data returned from the exchange for the specified date and time.")
        except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")

    def get_selected_datetime(self):
        try:
            combined_datetime = datetime.combine(self.selected_date, self.selected_time)
            # Ensure combined_datetime is timezone-aware
            if combined_datetime.tzinfo is None:
                combined_datetime = combined_datetime.replace(tzinfo=self.local_tz)
            else:
                combined_datetime = combined_datetime.astimezone(self.local_tz)
            # Convert to UTC
            return combined_datetime.astimezone(timezone.utc)
        except Exception as e:
            st.error(f"An error occurred while combining date and time: {e}")

    def trim_data(self, data, ema_10_df, ema_20_df, macd_df):
        trimmed_data = data.tail(self.limit)
        trimmed_ema_10_df = ema_10_df.tail(self.limit)
        trimmed_ema_20_df = ema_20_df.tail(self.limit)
        trimmed_macd_df = macd_df.tail(self.limit)

        trimmed_data = trimmed_data.copy()
        trimmed_data = trimmed_data.merge(trimmed_ema_10_df, on='date', how='left')
        trimmed_data = trimmed_data.merge(trimmed_ema_20_df, on='date', how='left')
        trimmed_data = trimmed_data.merge(trimmed_macd_df, on='date', how='left')
        return trimmed_data

    def setup_save_data(self):
        left, center, right = st.columns([1,2,3])
        self.filename_prefix = left.text_input("Enter Filename Prefix", value="", key="save_prefix_input")
        if st.button("Save Data"):
            self.save_data()

    def save_data(self):
        try:
            if st.session_state['data'] is not None:
                data_to_save = st.session_state['data']
                latest_candle_datetime = data_to_save['date'].iloc[-1]  # Get the timestamp of the latest fetched candle
                date_str = latest_candle_datetime.strftime('%Y-%m-%d')
                time_str = latest_candle_datetime.strftime('%H-%M-%S')
                prefix = self.filename_prefix.strip()  # Remove extra whitespace from the prefix
                
                filename = f"{prefix}_{self.symbol.replace('/', '_')}_{self.timeframe}_{date_str}_{time_str}.csv" if prefix else f"{self.symbol.replace('/', '_')}_{self.timeframe}_{date_str}_{time_str}.csv"
                
                save_dir = 'saved_data'
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                filepath = os.path.join(save_dir, filename)
                self.facade.save_data(data_to_save, self.saver, filepath)
                st.success(f"Data saved successfully as {filepath}!")
            else:
                st.error("No data to save. Please fetch data first.")
        except Exception as e:
            st.error(f"An error occurred while saving the data: {e}")
