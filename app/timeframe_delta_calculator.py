import re
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import streamlit as st

class TimeframeDeltaCalculator:
    """
    Responsible for converting timeframe strings (e.g. "1m", "4h", "1d") into timedelta or relativedelta objects.
    """
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
