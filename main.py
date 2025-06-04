import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

print("📦 Bot başlatılıyor...")

bot = TeleBot(TELEGRAM_BOT_TOKEN)
COIN_LIST_FILE = "coin_list_binance.txt"
BINANCE_URL = "https://api.binance.com/api/v3/klines"

def get_binance_data(symbol):
    params = {
        "symbol": symbol,
        "interval": "15m",
        "limit": 50
    }
    try:
        response = requests.get(BINANCE_URL, params=params)
        if response.status_code != 200:
            print(f"❌ {symbol} verisi alınamadı! HTTP: {response.status_code}")
            return None

        data = response.json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "_", "_", "_", "_", "_", "_"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        return df
    except Exception as e:
        print(f"⚠️ Hata ({symbol}): {e}")
        return None

def analyze_coin(symbol):
    df = get_binance_data(symbol)
    if df is None or len(df) < 30:
        return None

    df["ema20"] = EMAIndicator(close=df["close"], window=20).ema_indicator()
    df["macd"] = MACD(close=df["close"]).macd_diff()
    df["rsi"] = RSIIndicator(close=df["close"]).rsi()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    rsi_trend = "🔼" if last["rsi"] > 50 else "🔽"
    ema_trend = "🔼" if last["close"] > last["ema20"] else "🔽"
    macd_trend = "🔼" if last["macd"] > 0 else "🔽"
    trend_score = [rsi_trend, ema_trend, macd_trend].count("🔼")
    market_trend = "🚀 Boğa" if trend_score >= 2 else "🐻 Ayı"

    fiyat_degisim = ((last["close"] - prev["close"]) / prev["close"]) * 100
    hacim_degisim = ((last["volume"] - prev["volume"]) / prev["volume"]) * 100

    print(f"📊 {symbol}: Fiyat %{fiyat_degisim:.2f} | Hacim %{hacim_degisim:.2f}")

    if fiyat_degisim > 0.05 and hacim_degisim > 0.50:
        return f"📈 BALİNA SİNYALİ\n🪙 Coin: {symbol}\n💰 Fiyat: %{fiyat_degisim:.2f}\n📊 Hacim: %{hacim_degisim:.2f}\n{rsi_trend} RSI | {ema_trend} EMA | {macd_trend} MACD\n{market_trend}"

    return None

def send_telegram_message(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print("📤 Telegram mesajı gönderildi.")
    except Exception as e:
        print(f"📛 Telegram hatası: {e}")

def load_coin_list():
    try:
        with open(COIN_LIST_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"⚠️ Coin listesi yüklenemedi: {e}")
        return []

def main():
    print(f"🔁 Tarama başlıyor: {datetime.utcnow()}")
    coin_list = load_coin_list()
    sinyal_var = False

    for coin in coin_list:
        print(f"🔍 Analiz: {coin}")
        sinyal = analyze_coin(coin)
        if sinyal:
            send_telegram_message(sinyal)
            sinyal_var = True
        time.sleep(1)

    if not sinyal_var:
        send_telegram_message("📡 Tarama tamamlandı, sinyal bulunamadı.")

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"🚨 Döngü hatası: {e}")
        time.sleep(100)
