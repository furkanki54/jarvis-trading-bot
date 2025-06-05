import requests
import pandas as pd
import numpy as np

def get_binance_data(symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    if latest_rsi > 70:
        return "🔻 Ayı"
    elif latest_rsi < 30:
        return "🔺 Boğa"
    else:
        return "⚖️ Nötr"

def calculate_macd(df, short=12, long=26, signal=9):
    short_ema = df["close"].ewm(span=short, adjust=False).mean()
    long_ema = df["close"].ewm(span=long, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()

    if macd_line.iloc[-1] > signal_line.iloc[-1]:
        return "🔺 Boğa"
    else:
        return "🔻 Ayı"

def calculate_ema(df, short=50, long=200):
    short_ema = df["close"].ewm(span=short, adjust=False).mean()
    long_ema = df["close"].ewm(span=long, adjust=False).mean()

    if short_ema.iloc[-1] > long_ema.iloc[-1]:
        return "🔺 Boğa"
    else:
        return "🔻 Ayı"

def load_coin_list(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines()]
