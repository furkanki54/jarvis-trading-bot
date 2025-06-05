import requests
import pandas as pd
import numpy as np
import time
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

bot = TeleBot(TELEGRAM_BOT_TOKEN)

PRICE_THRESHOLD = 0.5
VOLUME_THRESHOLD = 50

def get_coin_list():
    with open("coin_list_binance.txt", "r") as f:
        return [line.strip() for line in f.readlines()]

def fetch_klines(symbol, interval='1h', limit=100):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def analyze_coin(symbol):
    data = fetch_klines(symbol)
    if not data or len(data) < 50:
        return None

    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])

    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    df['ema'] = EMAIndicator(df['close'], window=21).ema_indicator()
    macd = MACD(df['close'])
    df['macd'] = macd.macd_diff()

    last_close = df['close'].iloc[-1]
    prev_close = df['close'].iloc[-2]
    price_change = ((last_close - prev_close) / prev_close) * 100

    last_volume = df['volume'].iloc[-1]
    prev_volume = df['volume'].iloc[-2]
    volume_change = ((last_volume - prev_volume) / prev_volume) * 100

    rsi_trend = "Boğa" if df['rsi'].iloc[-1] > 50 else "Ayı"
    ema_trend = "Boğa" if last_close > df['ema'].iloc[-1] else "Ayı"
    macd_trend = "Boğa" if df['macd'].iloc[-1] > 0 else "Ayı"

    bull_points = sum([
        rsi_trend == "Boğa",
        ema_trend == "Boğa",
        macd_trend == "Boğa"
    ])
    overall = "Boğa" if bull_points >= 2 else "Ayı"

    return {
        "symbol": symbol,
        "price_change": round(price_change, 2),
        "volume_change": round(volume_change, 2),
        "rsi": rsi_trend,
        "ema": ema_trend,
        "macd": macd_trend,
        "overall": overall,
        "bull_points": bull_points
    }

def send_signal(analysis):
    msg = f"""📈 BALİNA SİNYALİ!
🌕 Coin: {analysis['symbol']}
💵 Fiyat Değişimi: %{analysis['price_change']}
🇹🇷 Hacim Değişimi: %{analysis['volume_change']}
🔼 {analysis['rsi']} | 🔼 {analysis['ema']} | 🔼 {analysis['macd']}
🚀 Genel Yön: {analysis['overall']} (Boğa Puanı: {analysis['bull_points']}/3)
"""
    bot.send_message(TELEGRAM_CHAT_ID, msg)

def run_bot():
    coin_list = get_coin_list()
    for symbol in coin_list:
        analysis = analyze_coin(symbol)
        if analysis and analysis["price_change"] > PRICE_THRESHOLD and analysis["volume_change"] > VOLUME_THRESHOLD:
            send_signal(analysis)
        time.sleep(1)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.strip().upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    analysis = analyze_coin(symbol)
    if analysis:
        msg = f"""🔍 Teknik Analiz Sonucu
🪙 Coin: {analysis['symbol']}
💵 Fiyat: %{analysis['price_change']}
📊 Hacim: %{analysis['volume_change']}
📈 RSI: {analysis['rsi']} | EMA: {analysis['ema']} | MACD: {analysis['macd']}
🌐 Genel Yön: {analysis['overall']} (Boğa Puanı: {analysis['bull_points']}/3)
"""
        bot.send_message(TELEGRAM_CHAT_ID, msg)
    else:
        bot.send_message(TELEGRAM_CHAT_ID, "📡 Teknik analiz tamamlandı, sinyal yok.")

if __name__ == "__main__":
    bot.polling()
