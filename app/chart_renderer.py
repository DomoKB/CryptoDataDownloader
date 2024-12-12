import pandas as pd
import streamlit as st
from lightweight_charts.widgets import StreamlitChart

class ChartRenderer:
    def display_chart(self, data: pd.DataFrame, symbol: str):
        try:
            chart = StreamlitChart(width=1024, height=576, inner_width=1, inner_height=0.75)
            chart.set(data)
            chart.time_scale(visible=False)
            chart.grid(vert_enabled=False, horz_enabled=False)
            chart.legend(visible=True, font_family="Arial", text=symbol)
            chart.fit()

            # Dynamically add any indicators that have been merged into data
            for col in data.columns:
                if col.startswith('ema_'):
                    line = chart.create_line(col, color='rgba(255, 235, 59, 0.6)', width=1,
                                                price_line=False, price_label=False)
                    line.set(data[['date', col]].dropna())

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
