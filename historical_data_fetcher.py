import os
import time
import requests
import pandas as pd
from datetime import datetime
from telebot import TeleBot

# Telegram ayarları
TELEGRAM_TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
CHAT_ID = "-1002549376225"
bot = TeleBot(TELEGRAM_TOKEN)

# Coin listesi
def load_coin_list():
    with open("coin_list.txt", "r") as file:
        return [line.strip().upper() for line in file]

coin_list = load_coin_list()

# Telegram sinyal fonksiyonu
def send_signal(message):
    try:
        bot.send_message(CHAT_ID, message)
        time.sleep(1.2)  # Telegram flood limitine karşı önlem
    except Exception as e:
        print(f"Telegram mesaj hatası: {e}")

# Binance'ten geçmiş veriyi çek
def fetch_historical_data(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1d&limit=1000"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if isinstance(data, list):
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            return df
        else:
            raise Exception(f"Veri formatı hatalı: {data}")
    except Exception as e:
        print(f"{symbol} verisi alınamadı: {e}")
        return None

# Veriyi kaydet
def save_all_data():
    if not os.path.exists("data"):
        os.makedirs("data")

    send_signal("📩 Veri çekme başladı...")

    for symbol in coin_list:
        df = fetch_historical_data(symbol)
        if df is not None:
            try:
                df.to_csv(f"data/{symbol}_1d.csv")
                send_signal(f"✅ {symbol} CSV kaydedildi.")
            except Exception as e:
                send_signal(f"⚠️ {symbol} için kayıt hatası: {e}")
        else:
            send_signal(f"❌ {symbol} için veri alınamadı.")
        time.sleep(1.5)  # Binance ve Telegram API için delay

# Başlat
if __name__ == "__main__":
    save_all_data()
