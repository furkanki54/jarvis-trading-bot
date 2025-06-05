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

def get_binance_data(symbol="BTCUSDT", interval="1h", limit=200):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ {symbol} verisi alınamadı! HTTP: {response.status_code}")
        return None
    raw_data = response.json()
    df = pd.DataFrame(raw_data, columns=["timestamp", "open", "high", "low", "close", "volume",
                                         "close_time", "quote_asset_volume", "trades",
                                         "taker_buy_base", "taker_buy_quote", "ignore"])
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df[["close", "volume"]]

def analyze_coin(symbol):
    df = get_binance_data(symbol)
    if df is None or len(df) < 50:
        return None

    df["ema20"] = EMAIndicator(close=df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(close=df["close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(close=df["close"], window=200).ema_indicator()
    df["macd"] = MACD(close=df["close"]).macd_diff()
    df["rsi"] = RSIIndicator(close=df["close"]).rsi()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    fiyat_degisim = ((last["close"] - prev["close"]) / prev["close"]) * 100
    hacim_degisim = ((last["volume"] - prev["volume"]) / prev["volume"]) * 100

    if last["rsi"] > 70:
        rsi_durum = "⚠️ Aşırı Alım"
    elif last["rsi"] < 30:
        rsi_durum = "⚠️ Aşırı Satım"
    elif last["rsi"] > 50:
        rsi_durum = "🔼 RSI Boğa"
    else:
        rsi_durum = "🔽 RSI Ayı"

    ema_durum = "🔼 EMA Boğa" if last["close"] > last["ema20"] else "🔽 EMA Ayı"
    macd_durum = "🔼 MACD Boğa" if last["macd"] > 0 else "🔽 MACD Ayı"

    cross_sinyali = ""
    if df["ema50"].iloc[-2] < df["ema200"].iloc[-2] and df["ema50"].iloc[-1] > df["ema200"].iloc[-1]:
        cross_sinyali = "✨ Golden Cross!"
    elif df["ema50"].iloc[-2] > df["ema200"].iloc[-2] and df["ema50"].iloc[-1] < df["ema200"].iloc[-1]:
        cross_sinyali = "⚠️ Death Cross!"

    boğa_puanı = sum([
        "Boğa" in rsi_durum,
        "Boğa" in ema_durum,
        "Boğa" in macd_durum
    ])
    piyasa_yonu = "🚀 Genel Yön: Boğa" if boğa_puanı >= 2 else "🐻 Genel Yön: Ayı"

    if fiyat_degisim > 0.25 and hacim_degisim > 1.0:
        return f"📈 BALİNA SİNYALİ!\n🪙 Coin: {symbol}\n💰 Fiyat Değişimi: %{fiyat_degisim:.2f}\n📊 Hacim Değişimi: %{hacim_degisim:.2f}\n\n{rsi_durum} | {ema_durum} | {macd_durum}\n{cross_sinyali}\n{piyasa_yonu}"

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
            return [line.strip().upper() for line in file.readlines() if line.strip()]
    except Exception as e:
        print(f"Coin listesi yüklenemedi: {e}")
        return []

def main():
    print("🔁 Coin tarama fonksiyonu çalışıyor.")
    coin_list = load_coin_list()
    sinyal_gonderildi = False

    for symbol in coin_list:
        print(f"⏳ Analiz: {symbol}")
        sinyal = analyze_coin(symbol)
        if sinyal:
            send_telegram_message(sinyal)
            sinyal_gonderildi = True
            time.sleep(1)

    if not sinyal_gonderildi:
        send_telegram_message("📡 Tarama tamamlandı, sinyale rastlanmadı.")

if __name__ == "__main__":
    while True:
        try:
            now = datetime.utcnow()
            if now.minute % 5 == 0 and now.second < 10:
                print(f"⏰ {now} – Tarama başlıyor...")
                main()
                time.sleep(60)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"🚨 Ana döngü hatası: {e}")
