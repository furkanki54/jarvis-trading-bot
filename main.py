import time
import requests
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from telebot import TeleBot
from datetime import datetime

# 🔐 Telegram Bot Bilgileri
TELEGRAM_BOT_TOKEN = '7759276451:AAF0Xphio-TjtYyFIzahQrG3fU-qdNQuBEw'
TELEGRAM_CHAT_ID = '-1002549376225'

bot = TeleBot(TELEGRAM_BOT_TOKEN)

# 🔎 Yardımcı fonksiyon: Coin listesini oku
def load_coin_list(file_path='coin_list_500_sample.txt'):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]

# 🔢 Yardımcı fonksiyon: Teknik analiz verilerini al ve hesapla
def get_coin_data(coin_id):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=2&interval=hourly'
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    prices = [x[1] for x in data['prices']]
    df = pd.DataFrame(prices, columns=['price'])
    df['rsi'] = RSIIndicator(df['price']).rsi()
    df['ema_20'] = EMAIndicator(df['price'], window=20).ema_indicator()
    macd = MACD(df['price'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    return df

# 🧠 Sinyal oluşturucu
def analyze_coin(coin_id):
    df = get_coin_data(coin_id)
    if df is None or len(df) < 30:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signals = []

    # RSI yorumu
    if last['rsi'] > 70:
        signals.append("🔻 RSI aşırı alımda (ayı)")
    elif last['rsi'] < 30:
        signals.append("🟢 RSI aşırı satımda (boğa)")

    # EMA yorumu
    if last['price'] > last['ema_20'] and prev['price'] < prev['ema_20']:
        signals.append("💚 EMA 20 üzerine çıkış (boğa sinyali)")
    elif last['price'] < last['ema_20'] and prev['price'] > prev['ema_20']:
        signals.append("🔴 EMA 20 altına iniş (ayı sinyali)")

    # MACD yorumu
    if last['macd'] > last['macd_signal'] and prev['macd'] < prev['macd_signal']:
        signals.append("📈 MACD kesişimi yukarı (boğa)")
    elif last['macd'] < last['macd_signal'] and prev['macd'] > prev['macd_signal']:
        signals.append("📉 MACD kesişimi aşağı (ayı)")

    # Kısa piyasa özeti
    if len(signals) >= 2:
        trend = "📊 Genel Görünüm: BOĞA 🟢" if "boğa" in " ".join(signals).lower() else "📊 Genel Görünüm: AYI 🔻"
        return f"📌 {coin_id.upper()} için sinyaller:\n" + "\n".join(signals) + f"\n{trend}"
    return None

# 📬 Telegram’a mesaj at
def send_telegram(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

# 🔁 Ana döngü
def run():
    coin_list = load_coin_list()
    for coin in coin_list:
        try:
            result = analyze_coin(coin)
            if result:
                send_telegram(result)
            time.sleep(3)
        except Exception as e:
            print(f"Hata {coin}: {e}")
            continue

if __name__ == "__main__":
    while True:
        print(f"[{datetime.now()}] Analiz başlatılıyor...")
        run()
        time.sleep(3600)  # Her saat başı çalışır
