import requests
from telebot import TeleBot
import time

# Telegram bot ayarları
TELEGRAM_TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
CHAT_ID = "-1002549376225"
bot = TeleBot(TELEGRAM_TOKEN)

print("⏳ Bot başlatılıyor...")

# 200+ coinlik özel liste (KISALTILMIŞ, senin liste tamdı)
coin_list = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "LTCUSDT",
    "DOTUSDT", "LINKUSDT", "WIFUSDT", "1000SHIBUSDT", "MATICUSDT", "OPUSDT", "ARBUSDT", "SUIUSDT", "PEPEUSDT",
    "JTOUSDT", "1000FLOKIUSDT", "PYTHUSDT", "ICPUSDT", "ARUSDT", "TIAUSDT", "BOMEUSDT", "INJUSDT"
    # Listeyi dilediğin kadar uzatabilirsin
]

# Binance verisi çek
def fetch_binance_klines(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1h&limit=100"
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

# Teknik analiz hesapla
def calculate_indicators(data):
    if not data or len(data) < 50:
        return None
    close_prices = [float(c[4]) for c in data]
    last_price = close_prices[-1]

    # RSI
    delta = [close_prices[i] - close_prices[i - 1] for i in range(1, len(close_prices))]
    gain = sum([d for d in delta if d > 0]) / 14
    loss = -sum([d for d in delta if d < 0]) / 14
    rs = gain / loss if loss != 0 else 0.01
    rsi = 100 - (100 / (1 + rs))

    # EMA
    ema20 = sum(close_prices[-20:]) / 20
    ema50 = sum(close_prices[-50:]) / 50

    # MACD Histogram
    ema12 = sum(close_prices[-12:]) / 12
    ema26 = sum(close_prices[-26:]) / 26
    macd = ema12 - ema26
    signal = macd  # sadeleştirilmiş
    histogram = macd - signal

    # Bollinger
    std_dev = (sum([(x - ema20)**2 for x in close_prices[-20:]]) / 20)**0.5
    upper_band = ema20 + (2 * std_dev)
    lower_band = ema20 - (2 * std_dev)
    bollinger = "Üst Bant" if last_price > upper_band else "Alt Bant" if last_price < lower_band else "Orta Bant"

    # Fibo
    high = max([float(c[2]) for c in data])
    low = min([float(c[3]) for c in data])
    diff = high - low
    fibo = {
        '0.236': round(high - diff * 0.236, 2),
        '0.382': round(high - diff * 0.382, 2),
        '0.5': round(high - diff * 0.5, 2),
        '0.618': round(high - diff * 0.618, 2),
        '0.786': round(high - diff * 0.786, 2)
    }

    return {
        "fiyat": round(last_price, 2),
        "rsi": round(rsi, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "macd_hist": round(histogram, 4),
        "bollinger": bollinger,
        "fibo": fibo
    }

# Yorum ve puan
def yorumla(rsi, ema20, ema50, macd_hist):
    puan = 0
    if rsi > 60: puan += 2
    elif rsi < 40: puan += 1
    if ema20 > ema50: puan += 2
    else: puan += 1
    if macd_hist > 0: puan += 2
    total_puan = round((puan / 6) * 10, 2)
    yorum = "📈 Boğa Gücü" if total_puan > 6 else "📉 Ayı Baskısı"
    return total_puan, yorum

# Mesaj gönder
def analiz_yap_ve_mesaj_gonder(symbol):
    data = fetch_binance_klines(symbol)
    indicators = calculate_indicators(data)
    if not indicators:
        bot.send_message(CHAT_ID, f"⚠️ {symbol} için veri alınamadı.")
        return
    puan, yorum = yorumla(indicators['rsi'], indicators['ema20'], indicators['ema50'], indicators['macd_hist'])
    fibo = indicators["fibo"]
    msg = f"""📊 Teknik Analiz: {symbol}
Fiyat: {indicators['fiyat']} USDT

🔹 RSI: {indicators['rsi']}
🔹 EMA20: {indicators['ema20']}
🔹 EMA50: {indicators['ema50']}
🔹 MACD Histogram: {indicators['macd_hist']}
🔹 Bollinger Durumu: {indicators['bollinger']}
🔹 Fibo Seviyeleri:
  - 0.236: {fibo['0.236']}
  - 0.382: {fibo['0.382']}
  - 0.5: {fibo['0.5']}
  - 0.618: {fibo['0.618']}
  - 0.786: {fibo['0.786']}

🎯 Ortalama Puan: {puan}/10
💬 Yorum: {yorum}
⚠️ AI Karar: {"Long açılır" if puan > 6 else "Short riski yüksek"}"""
    bot.send_message(CHAT_ID, msg)

# Komut yakalayıcı
@bot.message_handler(func=lambda message: message.text.upper().endswith("ANALİZ"))
def analiz_komutu(message):
    print(f"🧠 Komut geldi: {message.text}")
    coin = message.text.upper().replace(" ANALİZ", "")
    symbol = f"{coin}USDT"
    if symbol in coin_list:
        analiz_yap_ve_mesaj_gonder(symbol)
    else:
        bot.send_message(message.chat.id, f"❌ '{symbol}' desteklenmiyor.")

print("🚀 Bot polling'e geçti...")

# Bot başlat
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"💥 Hata: {e}")
        time.sleep(15)
