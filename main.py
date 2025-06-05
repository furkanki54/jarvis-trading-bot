import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from threading import Thread

bot = TeleBot(TELEGRAM_BOT_TOKEN)

COIN_LIST_FILE = "coin_list.txt"

def get_coin_data(symbol):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": "1h",
        "limit": 100
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
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
    except Exception as e:
        print(f"Veri çekme hatası ({symbol}): {e}")
        return None

def analyze_coin(symbol):
    df = get_coin_data(symbol)
    if df is None or len(df) < 20:
        return None

    df["ema20"] = EMAIndicator(close=df["close"], window=20).ema_indicator()
    df["macd"] = MACD(close=df["close"]).macd_diff()
    df["rsi"] = RSIIndicator(close=df["close"]).rsi()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    rsi_status = "🔼 Boğa" if last["rsi"] > 50 else "🔽 Ayı"
    ema_status = "🔼 Boğa" if last["close"] > last["ema20"] else "🔽 Ayı"
    macd_status = "🔼 Boğa" if last["macd"] > 0 else "🔽 Ayı"

    boğa_puanı = [rsi_status, ema_status, macd_status].count("🔼 Boğa")
    yön = "🚀 Genel Yön: Boğa" if boğa_puanı >= 2 else "🐻 Genel Yön: Ayı"

    fiyat_degisim = ((last["close"] - prev["close"]) / prev["close"]) * 100
    hacim_degisim = ((last["volume"] - prev["volume"]) / prev["volume"]) * 100

    if fiyat_degisim > 3 and hacim_degisim > 50:
        return f"📈 BALİNA SİNYALİ!\n🪙 Coin: {symbol.upper()}\n💰 Fiyat Değişimi: %{fiyat_degisim:.2f}\n📊 Hacim Değişimi: %{hacim_degisim:.2f}\n\n{rsi_status} | {ema_status} | {macd_status}\n{yön}"
    else:
        return f"🧪 Teknik Analiz ({symbol.upper()}):\n💰 Fiyat Değişimi: %{fiyat_degisim:.2f}\n📊 Hacim Değişimi: %{hacim_degisim:.2f}\n{rsi_status} | {ema_status} | {macd_status}\n{yön}"

def send_telegram_message(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print("📤 Telegram mesajı gönderildi.")
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")

def load_coin_list():
    try:
        with open(COIN_LIST_FILE, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except:
        return []

def main():
    print("🔁 Coin taraması başladı.")
    coin_list = load_coin_list()
    sinyal_var_mi = False

    for symbol in coin_list:
        print(f"📊 Tarama: {symbol}")
        sinyal = analyze_coin(symbol)
        if "BALİNA SİNYALİ" in str(sinyal):
            send_telegram_message(sinyal)
            sinyal_var_mi = True
            time.sleep(1)

    if not sinyal_var_mi:
        send_telegram_message("📡 Saatlik tarama yapıldı, sinyale rastlanmadı.")

# 👂 Telegram üzerinden kullanıcı mesajı ile analiz
@bot.message_handler(func=lambda message: True)
def handle_user_msg(message):
    symbol = message.text.strip().upper()
    if symbol.endswith("USDT"):
        sinyal = analyze_coin(symbol)
        if sinyal:
            bot.send_message(message.chat.id, f"📊 Kullanıcı Analizi:\n{sinyal}")
        else:
            bot.send_message(message.chat.id, f"❌ {symbol} için analiz yapılamadı.")
    else:
        bot.send_message(message.chat.id, "⛔ Lütfen geçerli bir coin girin. Örnek: `btcusdt`")

def start_polling():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    Thread(target=start_polling).start()
    while True:
        try:
            print(f"⏱ {datetime.utcnow()} - Yeni tarama başlatılıyor...")
            main()
        except Exception as e:
            print(f"🚨 Ana döngü hatası: {e}")
        time.sleep(3600)  # Her saat başı çalışır
