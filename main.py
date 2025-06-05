import time
import requests
import pandas as pd
from telebot import TeleBot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BINANCE_API_BASE, COIN_LIST_FILE
from utils import get_binance_data, calculate_rsi, calculate_macd, calculate_ema, load_coin_list

bot = TeleBot(TELEGRAM_TOKEN)
coin_list = load_coin_list(COIN_LIST_FILE)

VOLUME_THRESHOLD = 50  # % olarak
PRICE_THRESHOLD = 3  # % olarak

def check_coin(symbol):
    df = get_binance_data(symbol)
    if df is None or len(df) < 2:
        return None

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    price_change = ((latest["close"] - previous["close"]) / previous["close"]) * 100
    volume_change = ((latest["volume"] - previous["volume"]) / previous["volume"]) * 100

    signal = ""
    if price_change > PRICE_THRESHOLD and volume_change > VOLUME_THRESHOLD:
        signal = "📈 Fiyat ve hacimde yükseliş!"
    elif price_change < -PRICE_THRESHOLD and volume_change > VOLUME_THRESHOLD:
        signal = "📉 Fiyat düşüyor ama hacim artıyor!"
    elif volume_change > VOLUME_THRESHOLD:
        signal = "🐋 Yüksek hacim artışı tespit edildi!"

    if signal:
        rsi = calculate_rsi(df).iloc[-1]
        macd, signal_line = calculate_macd(df)
        macd_val = macd.iloc[-1]
        signal_val = signal_line.iloc[-1]
        ema = calculate_ema(df).iloc[-1]
        trend = "📊 Trend: Yukarı" if latest["close"] > ema else "📊 Trend: Aşağı"

        return f"🚨 Sinyal: {symbol}\n{signal}\n\nRSI: {rsi:.2f}\nMACD: {macd_val:.4f}\nEMA: {ema:.2f}\n{trend}"
    return None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.strip().upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    if symbol in coin_list:
        df = get_binance_data(symbol)
        if df is None:
            bot.reply_to(message, "Veri alınamadı.")
            return

        rsi = calculate_rsi(df).iloc[-1]
        macd, signal_line = calculate_macd(df)
        macd_val = macd.iloc[-1]
        signal_val = signal_line.iloc[-1]
        ema = calculate_ema(df).iloc[-1]
        latest_price = df.iloc[-1]["close"]
        trend = "Yukarı" if latest_price > ema else "Aşağı"

        score = 0
        if rsi < 30:
            score += 1
        elif rsi > 70:
            score -= 1
        if macd_val > signal_val:
            score += 1
        else:
            score -= 1
        if latest_price > ema:
            score += 1
        else:
            score -= 1

        bot.reply_to(message, f"📊 Teknik analiz: {symbol}\nRSI: {rsi:.2f}\nMACD: {macd_val:.4f}\nEMA: {ema:.2f}\nTrend: {trend}\nBoğa/Ayı Puanı: {score}/3")
    else:
        bot.reply_to(message, "Coin listede bulunamadı veya sembol hatalı.")

def run_loop():
    while True:
        for symbol in coin_list:
            try:
                message = check_coin(symbol)
                if message:
                    bot.send_message(TELEGRAM_CHAT_ID, message)
            except Exception as e:
                print(f"Hata oluştu: {symbol} - {str(e)}")
        time.sleep(60)

if __name__ == "__main__":
    run_loop()
