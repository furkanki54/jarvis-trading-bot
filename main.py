import requests
import pandas as pd
import time
from datetime import datetime
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from telebot import TeleBot

# Telegram bot ayarları
BOT_TOKEN = '7759276451:AAF0Xphio-TjtYyFIzahQrG3fU-qdNQuBEw'
CHAT_ID = '-1002549376225'
bot = TeleBot(BOT_TOKEN)

# Coin listesi
with open("coin_list_500_sample.txt", "r") as file:
    coin_list = [line.strip() for line in file.readlines()]

def fetch_ohlcv(coin_id, interval="1h"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval={interval}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if "prices" not in data or "total_volumes" not in data:
        return None

    prices = data["prices"]
    volumes = data["total_volumes"]
    df = pd.DataFrame({
        "time": [x[0] for x in prices],
        "close": [x[1] for x in prices],
        "volume": [x[1] for x in volumes]
    })
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

def analyze_coin(coin_id):
    df = fetch_ohlcv(coin_id)
    if df is None or df.shape[0] < 50:
        return None

    df["EMA_20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["EMA_50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["RSI"] = RSIIndicator(df["close"]).rsi()
    macd = MACD(df["close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    last_row = df.iloc[-1]

    signals = []

    if last_row["EMA_20"] > last_row["EMA_50"]:
        signals.append("📈 Golden Cross")

    if last_row["EMA_20"] < last_row["EMA_50"]:
        signals.append("📉 Death Cross")

    if last_row["RSI"] < 30:
        signals.append("🔻 Aşırı Satım (RSI<30)")

    if last_row["RSI"] > 70:
        signals.append("🔺 Aşırı Alım (RSI>70)")

    if last_row["MACD"] > last_row["MACD_signal"]:
        signals.append("💹 MACD Al Sinyali")

    if last_row["MACD"] < last_row["MACD_signal"]:
        signals.append("📉 MACD Sat Sinyali")

    # Anlık balina alımı
    if df.shape[0] >= 2:
        prev = df.iloc[-2]
        price_change = ((last_row["close"] - prev["close"]) / prev["close"]) * 100
        volume_change = ((last_row["volume"] - prev["volume"]) / prev["volume"]) * 100
        if price_change > 5 and volume_change > 30:
            signals.append("🐳 Balina Alımı Tespit Edildi!")

    if not signals:
        return None

    trend_comment = "📊 Genel Yorum: "
    if last_row["RSI"] > 55 and last_row["MACD"] > last_row["MACD_signal"] and last_row["EMA_20"] > last_row["EMA_50"]:
        trend_comment += "Boğa piyasası sinyalleri güçleniyor 🐂"
    elif last_row["RSI"] < 45 and last_row["MACD"] < last_row["MACD_signal"] and last_row["EMA_20"] < last_row["EMA_50"]:
        trend_comment += "Ayı piyasası baskısı hissediliyor 🐻"
    else:
        trend_comment += "Net bir yön sinyali yok ⚖️"

    message = f"📣 {coin_id.upper()} analiz sonucu:\n" + "\n".join(signals) + f"\n{trend_comment}"
    return message

def main():
    print("Tarama başladı...")
    all_signals = []

    for coin in coin_list:
        try:
            signal = analyze_coin(coin)
            if signal:
                bot.send_message(CHAT_ID, signal)
                all_signals.append(signal)
        except Exception as e:
            print(f"{coin} analizinde hata: {e}")

    if not all_signals:
        bot.send_message(CHAT_ID, "⏰ Saatlik tarama yapıldı, sinyale rastlanmadı.")

    print("Tarama tamamlandı.")
    time.sleep(3600)
    main()

if __name__ == "__main__":
    main()
