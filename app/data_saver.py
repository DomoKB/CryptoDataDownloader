from abc import ABC, abstractmethod
import pandas as pd
import streamlit as st

class DataSaverStrategy(ABC):
    @abstractmethod
    def save(self, data: pd.DataFrame, filename: str):
        pass

class CsvSaver(DataSaverStrategy):
    def save(self, data: pd.DataFrame, filename: str):
        try:
            data.to_csv(filename, index=False)
        except Exception as e:
            st.error(f"An error occurred while saving CSV: {e}")
