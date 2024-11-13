# Crypto Data Downloader

Crypto Data Downloader is an application that provides a streamlined interface for downloading and visualizing cryptocurrency data. Designed with a user-friendly frontend using Streamlit and candlestick charting through Lightweight Charts, this tool is ideal at providing data for machine learning, and trading analysis. The app currently supports Bybit and Binance exchanges and allows flexible selection of timeframes, trading pairs, and date ranges.

## Features
* Fetch historical OHLCV (Open, High, Low, Close, Volume) data from Binance and Bybit.
* Visualize cryptocurrency data with candlestick charts using Lightweight Charts.
* Support for various timeframes, trading pairs, and local time zone adjustments.
* Save data locally in CSV format for easy integration into machine learning workflows.

## Installation
### Conda Environment Setup
1. Clone the repository:

```
git clone https://github.com/DomoKB/CryptoDataDownloader.git
cd CryptoDataDownloader
```

2. Create and activate a new Conda environment:

```
conda create -n cdd python=3.12
conda activate cdd
```

3. Install required dependencies:

```
pip install -r requirements.txt
```

4. Run the application:

```
streamlit run main.py
```

### Non-Conda Setup

1. Clone the repository:

```
git clone https://github.com/DomoKB/CryptoDataDownloader.git
cd CryptoDataDownloader
```

2. Ensure Python 3.12 is installed, then install the required packages:

```
pip install -r requirements.txt
```

3. Run the application:

```
streamlit run main.py
```

### Visualising downloaded data

1. Run the application:

```
streamlit run csv_view.py
```

In the application, select a downloaded CSV data file.

### License
This project is licensed under the MIT License. See the LICENSE file for more details.
