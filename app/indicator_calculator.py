import pandas as pd
import pandas_ta as ta

class IndicatorCalculator:
    @staticmethod
    def calculate_ema(df: pd.DataFrame, length: int = 10) -> pd.DataFrame:
        """Calculate the EMA for the given period and return a DataFrame."""
        if df.empty:
            return pd.DataFrame()
        ema = ta.ema(df['close'], length=length)
        return pd.DataFrame({'date': df['date'], f'ema_{length}': ema})

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate the MACD signal line and return a DataFrame."""
        if df.empty:
            return pd.DataFrame()
        macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
        if macd is None or macd.empty:
            return pd.DataFrame()
        return pd.DataFrame({'date': df['date'], 'macd': macd['MACD_12_26_9']})
