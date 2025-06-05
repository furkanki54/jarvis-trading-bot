import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telebot import TeleBot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import time

bot = TeleBot(TELEGRAM_TOKEN)

with open("coin_list_binance.txt", "r") as f:
    coin_list = [line.strip().upper() for line in f if line.strip()]

def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    response = requests.get(url)
    data = response.json()
    if isinstance(data, list):
        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        return df
    return None

def analyze_coin(symbol):
    df = get_klines(symbol)
    if df is None or len(df) < 50:
        return None

    rsi = RSIIndicator(close=df["close"]).rsi()
    ema = EMAIndicator(close=df["close"], window=20).ema_indicator()
    macd = MACD(close=df["close"])
    macd_diff = macd.macd_diff()

    current_rsi = rsi.iloc[-1]
    current_ema = ema.iloc[-1]
    current_macd = macd_diff.iloc[-1]
    price = df["close"].iloc[-1]
    volume_now = df["volume"].iloc[-1]
    volume_before = df["volume"].iloc[-2]
    price_before = df["close"].iloc[-2]

    rsi_status = "🔼 Boğa" if current_rsi > 50 else "🔽 Ayı"
    ema_status = "🔼 Boğa" if price > current_ema else "🔽 Ayı"
    macd_status = "🔼 Boğa" if current_macd > 0 else "🔽 Ayı"

    fiyat_degisimi = ((price - price_before) / price_before) * 100
    hacim_degisimi = ((volume_now - volume_before) / volume_before) * 100

    boğa_puanı = [rsi_status, ema_status, macd_status].count("🔼 Boğa")

    sinyal_mesaj = f"""
📉 BALİNA SİNYALİ!
🌕 Coin: {symbol}
💲 Fiyat Değişimi: %{fiyat_degisimi:.2f}
📊 Hacim Değişimi: %{hacim_degisimi:.2f}
{rsi_status} | {ema_status} | {macd_status}
{'🚀 Genel Yön: Boğa' if boğa_puanı >= 2 else '🐻 Genel Yön: Ayı'} (Boğa Puanı: {boğa_puanı}/3)
"""
    if abs(hacim_degisimi) > 50 and abs(fiyat_degisimi) > 3:
        return sinyal_mesaj
    else:
        return None

def hourly_scan():
    sinyal_var_mi = False
    for coin in coin_list:
        try:
            sinyal = analyze_coin(coin)
            if sinyal:
                bot.send_message(TELEGRAM_CHAT_ID, sinyal)
                sinyal_var_mi = True
        except Exception as e:
            print(f"{coin} hatası: {e}")
    if not sinyal_var_mi:
        bot.send_message(TELEGRAM_CHAT_ID, "📡 Saatlik tarama yapıldı, sinyale rastlanmadı.")

@bot.message_handler(func=lambda message: True)
def handle_user_msg(message):
    symbol = message.text.strip().upper()
    if symbol.endswith("USDT"):
        try:
            sinyal = analyze_coin(symbol)
            if sinyal:
                bot.reply_to(message, sinyal)
            else:
                bot.reply_to(message, "📡 Teknik analiz tamamlandı, sinyal yok.")
        except Exception as e:
            bot.reply_to(message, f"Hata oluştu: {e}")

def start_polling():
    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as e:
            print("Polling hatası:", e)
            time.sleep(10)

if __name__ == "__main__":
    from threading import Thread
    Thread(target=start_polling).start()
    while True:
        hourly_scan()
        time.sleep(3600)
