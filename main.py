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

COIN_LIST_FILE = "coin_list_500_sample.txt"
BALINA_HACIM_ESIGI = 10  # %10 hacim artışı

def get_coin_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ {coin_id} verisi alınamadı! HTTP: {response.status_code}")
        return None
    data = response.json()
    prices = [x[1] for x in data["prices"]]
    volumes = [x[1] for x in data["total_volumes"]]
    timestamps = [x[0] for x in data["prices"]]

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps, unit="ms"),
        "price": prices,
        "volume": volumes
    })

    return df

def analyze_coin(coin_id):
    df = get_coin_data(coin_id)
    if df is None or len(df) < 20:
        return None

    df["ema20"] = EMAIndicator(close=df["price"], window=20).ema_indicator()
    df["macd"] = MACD(close=df["price"]).macd_diff()
    df["rsi"] = RSIIndicator(close=df["price"]).rsi()

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    rsi_durum = "🔼 Boğa" if last_row["rsi"] > 50 else "🔽 Ayı"
    ema_durum = "🔼 Boğa" if last_row["price"] > last_row["ema20"] else "🔽 Ayı"
    macd_durum = "🔼 Boğa" if last_row["macd"] > 0 else "🔽 Ayı"

    boğa_puanı = sum(x == "🔼 Boğa" for x in [rsi_durum, ema_durum, macd_durum])
    piyasa_yonu = "🚀 Genel Yön: Boğa" if boğa_puanı >= 2 else "🐻 Genel Yön: Ayı"

    fiyat_degisim = ((last_row["price"] - prev_row["price"]) / prev_row["price"]) * 100
    hacim_degisim = ((last_row["volume"] - prev_row["volume"]) / prev_row["volume"]) * 100

    if fiyat_degisim > 5 and hacim_degisim > BALINA_HACIM_ESIGI:
        return f"📈 BALİNA SİNYALİ!\n🪙 Coin: {coin_id.upper()}\n💰 Fiyat Değişimi: %{fiyat_degisim:.2f}\n📊 Hacim Değişimi: %{hacim_degisim:.2f}\n\n{rsi_durum} | {ema_durum} | {macd_durum}\n{piyasa_yonu}"

    return None

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("📤 Telegram mesajı gönderildi.")
    except Exception as e:
        print(f"Telegram hatası: {e}")

def load_coin_list():
    try:
        with open(COIN_LIST_FILE, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        print(f"Coin listesi yüklenemedi: {e}")
        return []

def main():
    print("🔁 Coin tarama fonksiyonu çalıştı.")
    coin_list = load_coin_list()
    sinyal_gonderildi = False

    for coin_id in coin_list:
        print(f"⏳ Analiz başlıyor: {coin_id}")
        sinyal = analyze_coin(coin_id)
        if sinyal:
            print(f"📬 Sinyal bulundu: {coin_id}")
            send_telegram_message(sinyal)
            sinyal_gonderildi = True
            time.sleep(1)

    if not sinyal_gonderildi:
        print("📭 Sinyal yok, Telegram'a bilgi verildi.")
        send_telegram_message("📡 Saatlik tarama yapıldı, sinyale rastlanmadı.")

if __name__ == "__main__":
    while True:
        now = datetime.utcnow()
        if now.minute == 0 and now.second < 10:
            print(f"✅ Tarama başlıyor: {now}")
            main()
            time.sleep(60)
        else:
            time.sleep(5)
