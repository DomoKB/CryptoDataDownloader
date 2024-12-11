import streamlit as st
import os
import ccxt
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, available_timezones
from lightweight_charts.widgets import StreamlitChart
from app.crypto_data_facade import CryptoDataFacade
from app.data_saver import CsvSaver

EXTRA_CANDLES = 100
SUPPORTED_EXCHANGES = {"binance": ccxt.binance(), "bybit": ccxt.bybit()}
SUPPORTED_TIMEFRAMES = {"binance": ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", '1M'], 
                        "bybit": ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d", "1w", '1M']}

class CryptoDataApp:
    def __init__(self):
        self.exchange_name = None
        self.symbol = None
        self.market_type = None
        self.timeframe = None
        self.limit = None
        self.selected_date = None
        self.selected_time = None
        self.facade = None
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
                self.display_chart()
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
        self.facade = CryptoDataFacade(SUPPORTED_EXCHANGES[self.exchange_name])

    def setup_market_type(self):
        if self.exchange_name == "bybit":
            self.market_type = st.selectbox("Select Market Type", ["spot", "perpetual"], index=1)
        else:
            self.market_type = "spot"

    def select_timeframe(self):
        try:
            # Get the list of supported timeframes for the selected exchange
            timeframes = SUPPORTED_TIMEFRAMES[self.exchange_name]
            
            # Set a default timeframe, e.g., "4h" if available, else the first option
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
                symbol=self.symbol, timeframe=self.timeframe, limit=self.limit + EXTRA_CANDLES,
                selected_datetime=self.get_selected_datetime(),
                local_tz=self.local_tz, market_type=self.market_type
            )
            if data is not None and not data.empty:
                ema_10_df = self.facade.calculate_indicator('ema', data, length=10)
                ema_20_df = self.facade.calculate_indicator('ema', data, length=20)
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

    def display_chart(self):
        try:
            data = st.session_state['data']
            chart = StreamlitChart(width=1024, height=576, inner_width=1, inner_height=0.75)
            chart.set(data)
            chart.time_scale(visible=False)
            chart.grid(vert_enabled=False, horz_enabled=False)
            chart.legend(visible=True, font_family="Arial", text=self.symbol)
            chart.fit()

            if 'ema_10' in data.columns:
                ema_10_line = chart.create_line('ema_10', color='rgba(255, 235, 59, 0.6)', width=1,
                                                price_line=False, price_label=False)
                ema_10_line.set(data[['date', 'ema_10']].dropna())

            if 'ema_20' in data.columns:
                ema_20_line = chart.create_line('ema_20', color='rgba(255, 152, 0, 0.6)', width=1,
                                                price_line=False, price_label=False)
                ema_20_line.set(data[['date', 'ema_20']].dropna())

            if 'macd' in data.columns:
                sub_chart = chart.create_subchart(width=1, height=0.25, sync=True)
                sub_chart.grid(vert_enabled=False, horz_enabled=False)
                sub_chart.legend(visible=True, font_family="Arial")
                macd_line = sub_chart.create_line('macd', color='rgba(41, 98, 255, 0.6)', width=1,
                                                  price_line=False, price_label=False)
                macd_line.set(data[['date', 'macd']].dropna())

            chart.load()
        except Exception as e:
            st.error(f"An error occurred while displaying the chart: {e}")

    def setup_save_data(self):
        left, center, right = st.columns([1,2,3])
        self.filename_prefix = left.text_input("Enter Filename Prefix", value="", key="save_prefix_input")
        if st.button("Save Data"):
            self.save_data()

    def save_data(self):
        try:
            if st.session_state['data'] is not None:
                data_to_save = st.session_state['data']
                saver = CsvSaver()
                latest_candle_datetime = data_to_save['date'].iloc[-1]  # Get the timestamp of the latest fetched candle
                date_str = latest_candle_datetime.strftime('%Y-%m-%d')
                time_str = latest_candle_datetime.strftime('%H-%M-%S')
                prefix = self.filename_prefix.strip()  # Remove extra whitespace from the prefix
                
                # Use the latest candle time instead of the selected date and time
                filename = f"{prefix}_{self.symbol.replace('/', '_')}_{self.timeframe}_{date_str}_{time_str}.csv" if prefix else f"{self.symbol.replace('/', '_')}_{self.timeframe}_{date_str}_{time_str}.csv"
                
                save_dir = 'saved_data'
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                filepath = os.path.join(save_dir, filename)
                self.facade.save_data(data_to_save, saver, filepath)
                st.success(f"Data saved successfully as {filepath}!")
            else:
                st.error("No data to save. Please fetch data first.")
        except Exception as e:
            st.error(f"An error occurred while saving the data: {e}")
