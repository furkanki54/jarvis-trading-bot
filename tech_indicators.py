import pandas as pd
import numpy as np
from binance import Client
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands

client = Client()

def get_ohlcv(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    return df

def get_rsi(symbol, interval):
    df = get_ohlcv(symbol, interval)
    rsi = RSIIndicator(df['close']).rsi().iloc[-1]
    if rsi > 70:
        return 0  # Aşırı alım
    elif rsi < 30:
        return 3  # Aşırı satım
    elif 45 <= rsi <= 55:
        return 2  # Nötr
    else:
        return 1  # Kararsız

def get_macd(symbol, interval):
    df = get_ohlcv(symbol, interval)
    macd = MACD(df['close'])
    macd_val = macd.macd_diff().iloc[-1]
    if macd_val > 0:
        return 3
    elif macd_val < 0:
        return 0
    else:
        return 1

def get_ema(symbol, interval):
    df = get_ohlcv(symbol, interval)
    ema = EMAIndicator(df['close'], window=20).ema_indicator().iloc[-1]
    price = df['close'].iloc[-1]
    if price > ema:
        return 3
    elif price < ema:
        return 0
    else:
        return 1

def get_bollinger_position(symbol, interval):
    df = get_ohlcv(symbol, interval)
    bb = BollingerBands(df['close'])
    last_close = df['close'].iloc[-1]
    upper = bb.bollinger_hband().iloc[-1]
    lower = bb.bollinger_lband().iloc[-1]

    if last_close >= upper:
        return "Üst Band (Aşırı Alım)"
    elif last_close <= lower:
        return "Alt Band (Aşırı Satım)"
    else:
        return "Orta Band"

def get_fibonacci_levels(symbol, interval):
    df = get_ohlcv(symbol, interval)
    high = df['high'].astype(float).max()
    low = df['low'].astype(float).min()

    levels = [
        high - (high - low) * ratio for ratio in [0.236, 0.382, 0.5, 0.618, 0.786]
    ]
    return levels
