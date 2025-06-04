import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BINANCE_API_BASE, COIN_LIST_FILE

print("📦 Bot başlatılıyor...")

bot = TeleBot(TELEGRAM_BOT_TOKEN)

def get_binance_data(symbol):
    url = f"{BINANCE_API_BASE}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1m",
        "limit": 3
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ {symbol} verisi alınamadı! HTTP: {response.status_code}")
        return None

    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "_",
        "_", "_", "_", "_", "_"
    ])
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df

def analyze_coin(symbol):
    df = get_binance_data(symbol)
    if df is None or len(df) < 3:
        return None

    df["ema"] = EMAIndicator(close=df["close"], window=3).ema_indicator()
    df["macd"] = MACD(close=df["close"]).macd_diff()
    df["rsi"] = RSIIndicator(close=df["close"]).rsi()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price_change = ((last["close"] - prev["close"]) / prev["close"]) * 100
    volume_change = ((last["volume"] - prev["volume"]) / prev["volume"]) * 100

    if price_change > 0.05 and volume_change > 0.5:
        return f"📈 SİNYAL: {symbol}\n💰 Fiyat: %{price_change:.2f}\n📊 Hacim: %{volume_change:.2f}\nRSI: {last['rsi']:.1f} MACD: {last['macd']:.2f} EMA: {last['ema']:.2f}"
    return None

def load_coin_list():
    try:
        with open(COIN_LIST_FILE, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        print(f"Liste yüklenemedi: {e}")
        return []

def send_message(msg):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, msg)
        print("📤 Telegram'a mesaj gönderildi.")
    except Exception as e:
        print(f"Telegram Hatası: {e}")

def main():
    print(f"🔁 Tarama başlatıldı: {datetime.utcnow()}")
    coin_list = load_coin_list()
    signal_sent = False

    for symbol in coin_list:
        print(f"🔍 İnceleniyor: {symbol}")
        result = analyze_coin(symbol)
        if result:
            send_message(result)
            signal_sent = True
            time.sleep(1)

    if not signal_sent:
        send_message("📡 Tarama tamamlandı, sinyal yok.")

if __name__ == "__main__":
    while True:
        try:
            main()
            time.sleep(60)
        except Exception as e:
            print(f"🚨 Ana hata: {e}")
            time.sleep(10)
"""

tools.display_dataframe_to_user(name="Dosya İçerikleri", dataframe=pd.DataFrame({
    "Dosya Adı": ["requirements.txt", "main.py"],
    "İçerik": [requirements.strip(), main_code.strip()]
}))
    
