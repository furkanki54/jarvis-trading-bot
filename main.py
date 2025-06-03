import time
import requests
import pandas as pd
import ta
from telebot import TeleBot

# Telegram ayarları
TELEGRAM_BOT_TOKEN = '7759276451:AAF0Xphio-TjtYyFIzahQrG3fU-qdNQuBEw'
TELEGRAM_CHAT_ID = '-1002549376225'
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Coin listesi
with open("coin_list_500_sample.txt", "r") as f:
    coin_list = [line.strip() for line in f.readlines()]

def send_telegram_message(message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as e:
        print("Telegram hatası:", e)

def get_ohlcv(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=2&interval=hourly"
    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame(data['prices'], columns=['time', 'price'])
    df['volume'] = [v[1] for v in data['total_volumes']]
    df['price'] = df['price'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['ema50'] = ta.trend.ema_indicator(df['price'], window=50)
    df['ema200'] = ta.trend.ema_indicator(df['price'], window=200)
    df['rsi'] = ta.momentum.rsi(df['price'], window=14)
    macd = ta.trend.macd_diff(df['price'])
    df['macd'] = macd
    return df

def analyze_coin(coin_id):
    try:
        df = get_ohlcv(coin_id)
        last = df.iloc[-1]

        rsi = last['rsi']
        macd = last['macd']
        ema50 = last['ema50']
        ema200 = last['ema200']
        price = last['price']
        volume_now = last['volume']
        volume_prev = df.iloc[-2]['volume']

        trend = "Boğa" if ema50 > ema200 else "Ayı"
        signal = []

        if rsi > 70:
            signal.append("🔴 Aşırı Alım (RSI > 70)")
        elif rsi < 30:
            signal.append("🟢 Aşırı Satım (RSI < 30)")

        if macd > 0:
            signal.append("📈 MACD Pozitif")
        else:
            signal.append("📉 MACD Negatif")

        if ema50 > ema200:
            signal.append("Golden Cross")
        elif ema50 < ema200:
            signal.append("Death Cross")

        hacim_degisim = ((volume_now - volume_prev) / volume_prev) * 100
        if hacim_degisim >= 30:
            signal.append(f"🐋 Balina Hacmi: %{round(hacim_degisim)}")

        if signal:
            mesaj = f"📊 {coin_id.upper()} Analizi:\n" + "\n".join(signal) + f"\n📉 Fiyat: ${price:.2f} | Trend: {trend}"
            send_telegram_message(mesaj)

    except Exception as e:
        print(f"{coin_id} analizi sırasında hata: {e}")

while True:
    for coin in coin_list:
        analyze_coin(coin)
        time.sleep(1)
    time.sleep(3600)
