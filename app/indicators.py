from abc import ABC, abstractmethod
import pandas as pd

class IndicatorStrategy(ABC):
    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

class EmaIndicator(IndicatorStrategy):
    def __init__(self, length: int):
        self.length = length

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        import pandas_ta as ta
        if df.empty:
            return pd.DataFrame()
        ema = ta.ema(df['close'], length=self.length)
        return pd.DataFrame({'date': df['date'], f'ema_{self.length}': ema})

class MacdIndicator(IndicatorStrategy):
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        import pandas_ta as ta
        if df.empty:
            return pd.DataFrame()
        macd = ta.macd(df['close'], fast=self.fast, slow=self.slow, signal=self.signal)
        if macd is None or macd.empty:
            return pd.DataFrame()
        return pd.DataFrame({'date': df['date'], 'macd': macd['MACD_12_26_9']})


class IndicatorRegistry:
    def __init__(self):
        self._indicators = {}

    def register(self, name: str, indicator: IndicatorStrategy):
        self._indicators[name] = indicator

    def get(self, name: str) -> IndicatorStrategy:
        if name not in self._indicators:
            raise ValueError(f"Indicator '{name}' is not registered.")
        return self._indicators[name]
