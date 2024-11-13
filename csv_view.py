import streamlit as st
import pandas as pd
from lightweight_charts.widgets import StreamlitChart

# Function to load CSV data
def load_csv():
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"], key="csv_upload")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        return df
    return None

# Function to display chart
def display_chart(data):
    if data is not None:
        # Create candlestick data
        candlestick_data = data[['date', 'open', 'high', 'low', 'close', 'volume']].dropna()
        
        # Create Streamlit Chart
        chart = StreamlitChart(width=1024, height=576, inner_width=1, inner_height=0.75)
        chart.set(candlestick_data)
        chart.time_scale(visible=False)
        chart.grid(vert_enabled=False, horz_enabled=False)
        chart.legend(visible=True, font_family="Arial", text="Candlestick Chart")
        chart.fit()

        # Plot EMA 10 line if available
        if 'ema_10' in data.columns:
            ema_10_line = chart.create_line('ema_10', color='rgba(255, 235, 59, 0.6)', width=1,
                                            price_line=False, price_label=False)
            ema_10_line.set(data[['date', 'ema_10']].dropna())

        # Plot EMA 20 line if available
        if 'ema_20' in data.columns:
            ema_20_line = chart.create_line('ema_20', color='rgba(255, 152, 0, 0.6)', width=1,
                                            price_line=False, price_label=False)
            ema_20_line.set(data[['date', 'ema_20']].dropna())

        # Plot MACD if available
        if 'macd' in data.columns:
            sub_chart = chart.create_subchart(width=1, height=0.25, sync=True)
            sub_chart.grid(vert_enabled=False, horz_enabled=False)
            sub_chart.legend(visible=True, font_family="Arial")
            macd_line = sub_chart.create_line('macd', color='rgba(41, 98, 255, 0.6)', width=1,
                                              price_line=False, price_label=False)
            macd_line.set(data[['date', 'macd']].dropna())

        chart.load()

# Main Streamlit app
def main():
    st.set_page_config(layout="wide")
    st.subheader("Cryptocurrency Data Visualization")

    # Load CSV data
    data = load_csv()
    if data is not None:
        st.success("CSV file loaded successfully!")
        display_chart(data)
    else:
        st.warning("Please upload a CSV file to display the data.")

if __name__ == "__main__":
    main()
