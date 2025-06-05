import requests
import pandas as pd
import numpy as np
from datetime import datetime

def get_binance_data(symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Veri çekme hatası {symbol}: {e}")
        return None

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast).mean()
    ema_slow = df['close'].ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd.iloc[-1], signal_line.iloc[-1]

def calculate_ema(df, period=50):
    return df['close'].ewm(span=period).mean().iloc[-1]

def load_coin_list(filename):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f.readlines() if line.strip()]

def analyze_indicators(symbol, rsi, macd, ema):
    messages = []
    score = 0

    if rsi > 70:
        messages.append("⚠️ RSI aşırı alım bölgesinde.")
        score -= 1
    elif rsi < 30:
        messages.append("✅ RSI aşırı satım bölgesinde.")
        score += 1

    if macd > 0:
        messages.append("📈 MACD pozitif bölgede (al sinyali).")
        score += 1
    else:
        messages.append("📉 MACD negatif bölgede (sat sinyali).")
        score -= 1

    if score >= 2:
        messages.append("🔔 Genel sinyal: GÜÇLÜ AL")
    elif score <= -2:
        messages.append("🔻 Genel sinyal: GÜÇLÜ SAT")
    else:
        messages.append("➖ Genel sinyal: NÖTR")

    return f"*{symbol} Teknik Analiz:*\n" + "\n".join(messages)

def analyze_price_volume(symbol, df, price_threshold=3, volume_threshold=50):
    close_now = df['close'].iloc[-1]
    close_prev = df['close'].iloc[-2]
    price_change = ((close_now - close_prev) / close_prev) * 100

    volume_now = df['volume'].iloc[-1]
    volume_prev = df['volume'].iloc[-2]
    volume_change = ((volume_now - volume_prev) / (volume_prev + 1e-10)) * 100

    messages = []

    if abs(price_change) >= price_threshold and volume_change >= volume_threshold:
        direction = "yükseldi" if price_change > 0 else "düştü"
        messages.append(
            f"🚨 {symbol} son mumda %{price_change:.2f} {direction}, hacim %{volume_change:.2f} arttı."
        )
        messages.append("🐋 Balina hareketi olabilir!")

    return "\n".join(messages)
