import telebot
import requests
import pandas as pd

TOKEN = "8078903959:AAF37zwfzT1lJXqgob_3bCxEeiDgbRSow3w"
bot = telebot.TeleBot(TOKEN)

# Binance veri çekme
def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    closes = [float(entry[4]) for entry in data]
    return closes

# RSI hesapla
def get_rsi_score(closes):
    prices = pd.Series(closes)
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    if latest_rsi > 70:
        return 0
    elif latest_rsi > 60:
        return 1
    elif latest_rsi > 50:
        return 2
    else:
        return 3

# EMA hesapla
def get_ema_score(closes):
    prices = pd.Series(closes)
    ema_20 = prices.ewm(span=20).mean().iloc[-1]
    ema_50 = prices.ewm(span=50).mean().iloc[-1]
    ema_200 = prices.ewm(span=200).mean().iloc[-1]
    current = prices.iloc[-1]
    score = 0
    if current > ema_200:
        score += 1
    if current > ema_50:
        score += 1
    if current > ema_20:
        score += 1
    return score

# MACD hesapla (teknik analiz botundan birebir alındı)
def calculate_macd(close_prices, fast=12, slow=26, signal=9):
    prices = pd.Series(close_prices)
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return float(macd_line.iloc[-1]), float(signal_line.iloc[-1]), float(histogram.iloc[-1])

# MACD puanla (geliştirilmiş)
def score_macd(macd_line, signal_line, histogram):
    if macd_line > signal_line and histogram > 0:
        if histogram > 50:
            return 3
        elif histogram > 20:
            return 2
        else:
            return 1
    elif macd_line < signal_line and histogram < 0:
        if histogram < -50:
            return 0
        elif histogram < -20:
            return 1
        else:
            return 2
    else:
        return 1

# Ana analiz fonksiyonu
def analyze_coin(symbol):
    timeframes = ["15m", "1h", "4h", "1d"]
    rsi_scores = []
    macd_scores = []
    ema_scores = []

    for tf in timeframes:
        try:
            closes = get_klines(symbol, tf)
            closes_series = pd.Series(closes)

            rsi = get_rsi_score(closes)
            macd_line, signal_line, hist = calculate_macd(closes_series)
            macd = score_macd(macd_line, signal_line, hist)
            ema = get_ema_score(closes)

            rsi_scores.append(rsi)
            macd_scores.append(macd)
            ema_scores.append(ema)
        except Exception as e:
            print(f"{symbol} {tf} hatası: {e}")
            rsi_scores.append(0)
            macd_scores.append(0)
            ema_scores.append(0)

    ortalama_puan = round((sum(rsi_scores) + sum(macd_scores) + sum(ema_scores)) / 12, 2)

    if ortalama_puan >= 7:
        yorum = "🐂 Boğa piyasası"
    elif ortalama_puan <= 3:
        yorum = "🐻 Ayı piyasası"
    else:
        yorum = "⚖️ Kararsız bölge"

    try:
        fiyat = float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()["price"])
    except:
        fiyat = 0.0

    mesaj = f"""📊 Teknik Analiz: {symbol}
Fiyat: {fiyat} USDT
———————————————
🔹 RSI Puanları: {rsi_scores}
🔹 MACD Puanları: {macd_scores}
🔹 EMA Puanları: {ema_scores}
———————————————
🎯 Ortalama Puan: {ortalama_puan}/10
💬 Yorum: {yorum}
"""
    return mesaj

# Telegram mesaj dinleyici
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip().upper()
    if text.endswith("USDT"):
        reply = analyze_coin(text)
        bot.send_message(message.chat.id, reply)

# Bot başlat
if __name__ == "__main__":
    bot.polling()
