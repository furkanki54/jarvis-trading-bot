import os
import time
import pandas as pd
from datetime import datetime
from telebot import TeleBot
from ai_historical_analyzer import analyze_historical_similarity
from config import TELEGRAM_TOKEN, CHAT_ID

bot = TeleBot(TELEGRAM_TOKEN)

def load_coin_list():
    with open("coin_list.txt", "r") as f:
        return [line.strip().upper() for line in f.readlines()]

def send_telegram_message(message):
    bot.send_message(CHAT_ID, message)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_gain = up.rolling(window=period).mean()
    avg_loss = down.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period):
    return prices.ewm(span=period, adjust=False).mean()

def calculate_macd(prices):
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return histogram

def calculate_bollinger_bands(prices, period=20):
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    return upper, lower

def calculate_fibonacci_levels(prices):
    recent = prices.tail(50)
    max_price = recent.max()
    min_price = recent.min()
    diff = max_price - min_price
    levels = {
        "0.236": max_price - diff * 0.236,
        "0.382": max_price - diff * 0.382,
        "0.5": max_price - diff * 0.5,
        "0.618": max_price - diff * 0.618,
        "0.786": max_price - diff * 0.786
    }
    return levels

def analyze_coin(symbol):
    try:
        df = pd.read_csv(f"data/{symbol}_1d.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)

        close_prices = df["close"].astype(float)
        if len(close_prices) < 100:
            return None

        rsi = calculate_rsi(close_prices).iloc[-1]
        ema20 = calculate_ema(close_prices, 20).iloc[-1]
        ema50 = calculate_ema(close_prices, 50).iloc[-1]
        macd_hist = calculate_macd(close_prices).iloc[-1]
        upper_band, lower_band = calculate_bollinger_bands(close_prices)
        boll_status = "Üst Bant" if close_prices.iloc[-1] > upper_band.iloc[-1] else "Alt Bant" if close_prices.iloc[-1] < lower_band.iloc[-1] else "Orta Bant"
        fibo = calculate_fibonacci_levels(close_prices)

        history_comment = analyze_historical_similarity(symbol)

        price = close_prices.iloc[-1]
        score = 0
        if rsi > 60: score += 2
        elif rsi < 40: score += 0
        else: score += 1
        if macd_hist > 0: score += 2
        else: score += 0
        if price > ema20 and price > ema50: score += 2
        elif price > ema20: score += 1
        score_total = round((score / 6) * 10, 2)

        trend = "Yatay Konsolidasyon"
        if price > ema20 and price > ema50:
            trend = "Yukarı Yönlü"
        elif price < ema20 and price < ema50:
            trend = "Aşağı Yönlü"

        msg = f"""
📊 Teknik Analiz: {symbol}
Fiyat: {price:.2f} USDT

🔹 RSI: {rsi:.2f}
🔹 EMA20 / EMA50: {ema20:.2f} / {ema50:.2f}
🔹 MACD Histogram: {macd_hist:.4f}
🔹 Bollinger Durumu: {boll_status}
🔹 Fibo Seviyeleri:
  - 0.236: {fibo['0.236']:.2f}
  - 0.382: {fibo['0.382']:.2f}
  - 0.5: {fibo['0.5']:.2f}
  - 0.618: {fibo['0.618']:.2f}
  - 0.786: {fibo['0.786']:.2f}

📈 Trend: {trend}
🎯 Ortalama Puan: {score_total}/10

📍 AI Taktik Not:
{history_comment}
        """
        return msg.strip()
    except Exception as e:
        return f"⚠️ {symbol} için analiz hatası: {e}"

def main():
    while True:
        coin_list = load_coin_list()
        for symbol in coin_list:
            msg = analyze_coin(symbol)
            if msg:
                send_telegram_message(msg)
                time.sleep(1)
        print("✅ Tüm coinler analiz edildi. 1 saat bekleniyor...")
        time.sleep(3600)

if __name__ == "__main__":
    main()
