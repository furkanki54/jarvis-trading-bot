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

def get_coin_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval=1h&limit=50"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ {symbol} verisi alınamadı! HTTP: {response.status_code}")
        return None
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["price"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    return df[["timestamp", "price", "volume"]]

def analyze_coin(symbol):
    df = get_coin_data(symbol)
    if df is None or len(df) < 30:
        return None

    df["ema50"] = EMAIndicator(close=df["price"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(close=df["price"], window=200, fillna=True).ema_indicator()
    df["macd"] = MACD(close=df["price"]).macd()
    df["macd_signal"] = MACD(close=df["price"]).macd_signal()
    df["rsi"] = RSIIndicator(close=df["price"]).rsi()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Golden / Death Cross
    if last["ema50"] > last["ema200"]:
        cross_status = "🔔 Golden Cross: EMA50 > EMA200"
    elif last["ema50"] < last["ema200"]:
        cross_status = "⚠️ Death Cross: EMA50 < EMA200"
    else:
        cross_status = "➖ Kesişim Yok"

    # RSI Yorumu
    if last["rsi"] > 70:
        rsi_comment = "🔴 Aşırı Alım"
    elif last["rsi"] < 30:
        rsi_comment = "🟢 Aşırı Satım"
    else:
        rsi_comment = "⚪ Nötr"

    # MACD Yorumu
    macd_comment = "🔼 MACD Pozitif" if last["macd"] > last["macd_signal"] else "🔽 MACD Negatif"

    # Boğa/Ayı puanı (maksimum 5)
    bull_score = 0
    bull_score += 1 if last["rsi"] > 50 else 0
    bull_score += 1 if last["ema50"] > last["ema200"] else 0
    bull_score += 1 if last["macd"] > last["macd_signal"] else 0
    bull_score += 1 if last["rsi"] < 70 else 0
    bull_score += 1 if last["rsi"] > 30 else 0
    trend_label = "🚀 Güçlü Boğa" if bull_score >= 4 else ("🐂 Orta Boğa" if bull_score == 3 else "🐻 Ayı Eğilimi")

    # Fiyat ve hacim değişimi
    price_change = ((last["price"] - prev["price"]) / prev["price"]) * 100
    volume_change = ((last["volume"] - prev["volume"]) / prev["volume"]) * 100

    if price_change > 0.5 and volume_change > 0.05:
        message = f"""📊 Teknik Analiz Özeti – {symbol.upper()}
💰 Fiyat: ${last['price']:.2f}
📉 Hacim: {last['volume']:.2f}

📍 RSI: {last['rsi']:.2f} → {rsi_comment}
📍 {cross_status}
📍 {macd_comment}

🎯 Puanlama: {bull_score}/5 → {trend_label}
📅 Tarih: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"""

        return message

    return None

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("📤 Telegram mesajı gönderildi.")
    except Exception as e:
        print(f"Telegram hatası: {e}")

def load_coin_list():
    try:
        with open(COIN_LIST_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Coin listesi yüklenemedi: {e}")
        return []

def main():
    print("🔁 Tarama başlatıldı...")
    coin_list = load_coin_list()
    sinyal_geldi = False

    for coin in coin_list:
        print(f"⏳ {coin} analiz ediliyor...")
        sinyal = analyze_coin(coin)
        if sinyal:
            send_telegram_message(sinyal)
            sinyal_geldi = True
            time.sleep(1)

    if not sinyal_geldi:
        send_telegram_message("📡 Tarama yapıldı, sinyale rastlanmadı.")

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"🚨 Ana döngü hatası: {e}")
        time.sleep(60)  # her 1 dakikada bir çalışır
