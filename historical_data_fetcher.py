import os
import time
import requests
import pandas as pd
from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID
from telebot import TeleBot

# Telegram bot ayarı
bot = TeleBot(TELEGRAM_TOKEN)

# Coin listesi
def load_coin_list():
    with open("coin_list.txt", "r") as f:
        return [line.strip().upper() for line in f.readlines()]

coin_list = load_coin_list()

# 📁 CSV klasörü oluştur (eksikse)
os.makedirs("data", exist_ok=True)

# Telegram mesaj gönder
def send_signal(message):
    bot.send_message(CHAT_ID, message)

# Binance'ten 1d veri çek
def fetch_klines(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1d&limit=1000"
    response = requests.get(url)
    return response.json()

# ⛏️ Her coin için veri çek ve CSV olarak kaydet
def save_all_data():
    for symbol in coin_list:
        try:
            data = fetch_klines(symbol)
            if not data:
                send_signal(f"⚠️ {symbol} verisi boş.")
                continue

            df = pd.DataFrame(data, columns=[
                "time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "trades",
                "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
            ])
            df["time"] = pd.to_datetime(df["time"], unit="ms")
            df.to_csv(f"data/{symbol}_1d.csv", index=False)
            send_signal(f"✅ {symbol} CSV kaydedildi.")
            time.sleep(1)
        except Exception as e:
            send_signal(f"❌ {symbol} için hata: {str(e)}")

if __name__ == "__main__":
    send_signal("📥 Veri çekme başladı...")
    save_all_data()
    send_signal("📁 Tüm veriler kaydedildi.")
