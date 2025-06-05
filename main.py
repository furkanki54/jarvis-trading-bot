import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

print("🚀 Bot başlatılıyor...")
bot = TeleBot(TELEGRAM_BOT_TOKEN)

COIN_LIST_FILE = "coin_list_binance.txt"
THRESHOLD_FIYAT = 0.1  # %0.1
THRESHOLD_HACIM = 1    # %1

def get_binance_ohlcv(symbol):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": "1h",
        "limit": 100
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ {symbol} verisi alınamadı.")
        return None
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df[["timestamp", "close", "volume"]]

def teknik_analiz(df):
    df["ema20"] = EMAIndicator(close=df["close"], window=20).ema_indicator()
    df["macd"] = MACD(close=df["close"]).macd_diff()
    df["rsi"] = RSIIndicator(close=df["close"]).rsi()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    fiyat_degisim = ((last["close"] - prev["close"]) / prev["close"]) * 100
    hacim_degisim = ((last["volume"] - prev["volume"]) / prev["volume"]) * 100

    rsi_durum = "🔼 Boğa" if last["rsi"] > 50 else "🔽 Ayı"
    ema_durum = "🔼 Boğa" if last["close"] > last["ema20"] else "🔽 Ayı"
    macd_durum = "🔼 Boğa" if last["macd"] > 0 else "🔽 Ayı"

    boğa_puani = sum(x == "🔼 Boğa" for x in [rsi_durum, ema_durum, macd_durum])
    piyasa_yonu = "🚀 Genel Yön: Boğa" if boğa_puani >= 2 else "🐻 Genel Yön: Ayı"

    analiz = (
        f"🪙 Coin: {df.name}\n"
        f"💰 Fiyat Değişimi: %{fiyat_degisim:.2f}\n"
        f"📊 Hacim Değişimi: %{hacim_degisim:.2f}\n"
        f"{rsi_durum} | {ema_durum} | {macd_durum}\n"
        f"{piyasa_yonu} (Boğa Puanı: {boğa_puani}/3)"
    )

    if fiyat_degisim > THRESHOLD_FIYAT and hacim_degisim > THRESHOLD_HACIM:
        analiz = "📈 BALİNA SİNYALİ!\n" + analiz

    return analiz if "BALİNA SİNYALİ" in analiz else None

def send_message(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print("📤 Telegram mesajı gönderildi.")
    except Exception as e:
        print(f"Telegram hatası: {e}")

def coin_listesi_yukle():
    try:
        with open(COIN_LIST_FILE, "r") as f:
            return [line.strip().upper() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"📂 Coin listesi yüklenemedi: {e}")
        return []

def main_loop():
    print(f"🔁 Tarama başladı: {datetime.now()}")
    coin_list = coin_listesi_yukle()
    sinyal_var = False

    for coin in coin_list:
        df = get_binance_ohlcv(coin)
        if df is None or len(df) < 30:
            continue
        df.name = coin
        mesaj = teknik_analiz(df)
        if mesaj:
            send_message(mesaj)
            sinyal_var = True
        time.sleep(1)

    if not sinyal_var:
        send_message("📡 Saatlik tarama tamamlandı, sinyal bulunamadı.")

@bot.message_handler(func=lambda msg: True)
def manuel_analiz(mesaj):
    coin = mesaj.text.strip().upper()
    if not coin.endswith("USDT"):
        return
    df = get_binance_ohlcv(coin)
    if df is None or len(df) < 30:
        bot.reply_to(mesaj, f"❌ {coin} verisi alınamadı.")
        return
    df.name = coin
    analiz = teknik_analiz(df)
    bot.reply_to(mesaj, analiz if analiz else "📭 Teknik analiz tamamlandı, sinyal yok.")

if __name__ == "__main__":
    import threading
    threading.Thread(target=bot.polling, daemon=True).start()
    while True:
        try:
            main_loop()
            time.sleep(3600)  # 1 saatte bir tarama
        except Exception as e:
            print(f"🚨 Ana döngü hatası: {e}")
            time.sleep(60)
