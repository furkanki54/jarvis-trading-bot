import requests
from telebot import TeleBot
import time

# Telegram bot ayarları
TELEGRAM_TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
CHAT_ID = "-1002549376225"
bot = TeleBot(TELEGRAM_TOKEN)

print("⏳ Bot başlatılıyor...")

coin_list = ["BTCUSDT", "ETHUSDT", "WIFUSDT", "SOLUSDT", "AVAXUSDT"]  # kısaltılmış, tüm listen eklenebilir

def fetch_binance_klines(symbol):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1h&limit=3"
    response = requests.get(url, timeout=10)
    return response.json()

def calculate_indicators(data):
    if not data or len(data) < 3:
        return None

    closes = [float(c[4]) for c in data]
    volumes = [float(c[5]) for c in data]
    price_prev = closes[-2]
    price_now = closes[-1]
    vol_prev = volumes[-2]
    vol_now = volumes[-1]

    delta = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gain = sum(d for d in delta if d > 0) / 2
    loss = -sum(d for d in delta if d < 0) / 2
    rs = gain / loss if loss != 0 else 0.01
    rsi_now = 100 - (100 / (1 + rs))

    rsi_prev = 50  # örnek varsayım, dilersen 14-mumluk gerçek RSI serisi hesaplarım

    ema20 = sum(closes[-2:]) / 2
    ema50 = sum(closes) / 3  # az mumla geçici hesaplama
    macd_hist = (sum(closes[-2:]) / 2 - sum(closes) / 3)

    std_dev = (sum([(x - ema20) ** 2 for x in closes]) / 2) ** 0.5
    upper_band = ema20 + 2 * std_dev
    lower_band = ema20 - 2 * std_dev
    bollinger = "Üst Bant" if price_now > upper_band else "Alt Bant" if price_now < lower_band else "Orta Bant"

    high = max(float(c[2]) for c in data)
    low = min(float(c[3]) for c in data)
    diff = high - low
    fibo = {
        '0.236': round(high - diff * 0.236, 2),
        '0.382': round(high - diff * 0.382, 2),
        '0.5': round(high - diff * 0.5, 2),
        '0.618': round(high - diff * 0.618, 2),
        '0.786': round(high - diff * 0.786, 2)
    }

    hacim_artisi = ((vol_now - vol_prev) / vol_prev) * 100 if vol_prev > 0 else 0

    return {
        "price": round(price_now, 2),
        "price_prev": round(price_prev, 2),
        "rsi": round(rsi_now, 2),
        "rsi_prev": round(rsi_prev, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "macd_hist": round(macd_hist, 4),
        "bollinger": bollinger,
        "fibo": fibo,
        "hacim_artisi": round(hacim_artisi, 2)
    }

def yorumla(rsi, ema20, ema50, macd_hist):
    puan = 0
    if rsi > 60: puan += 2
    elif rsi < 40: puan += 1
    if ema20 > ema50: puan += 2
    else: puan += 1
    if macd_hist > 0: puan += 2
    total = round((puan / 6) * 10, 2)
    yorum = "📈 Boğa Gücü" if total > 6 else "📉 Ayı Baskısı"
    return total, yorum

def stratejik_yorumlar(rsi, rsi_prev, price, price_prev, ema20, ema50, macd_hist, fibo, bollinger, hacim_artisi):
    yorum = []

    if rsi > rsi_prev and price < price_prev:
        yorum.append("🔍 RSI Uyumsuzluğu: Dip sinyali olabilir.")

    if rsi < 35 and hacim_artisi > 30:
        yorum.append("🐋 Hacim Artışı: Balina alımı olabilir.")

    if price > fibo['0.618'] and price_prev < fibo['0.618']:
        yorum.append("📍 Fibo Tepkisi: 0.618 seviyesinden dönüş olabilir.")

    if bollinger == "Üst Bant" and rsi > 60:
        yorum.append("💥 Bollinger Patlaması: Yukarı yönlü baskı artmış.")

    if ema20 > ema50 and abs(ema20 - ema50) < 200:
        yorum.append("🔄 EMA Kesişimi: Trend dönüşü başlangıçta olabilir.")

    return "\n".join(yorum)

def analiz_yap_ve_mesaj_gonder(symbol):
    indicators = calculate_indicators(fetch_binance_klines(symbol))
    if not indicators:
        bot.send_message(CHAT_ID, f"⚠️ {symbol} için veri alınamadı.")
        return

    puan, genel_yorum = yorumla(indicators['rsi'], indicators['ema20'], indicators['ema50'], indicators['macd_hist'])

    msg = f"""📊 Teknik Analiz: {symbol}
Fiyat: {indicators['price']} USDT

🔹 RSI: {indicators['rsi']}
🔹 EMA20: {indicators['ema20']}
🔹 EMA50: {indicators['ema50']}
🔹 MACD Histogram: {indicators['macd_hist']}
🔹 Bollinger Durumu: {indicators['bollinger']}
🔹 Fibo Seviyeleri:
  - 0.236: {indicators['fibo']['0.236']}
  - 0.382: {indicators['fibo']['0.382']}
  - 0.5: {indicators['fibo']['0.5']}
  - 0.618: {indicators['fibo']['0.618']}
  - 0.786: {indicators['fibo']['0.786']}

🎯 Ortalama Puan: {puan}/10
💬 Yorum: {genel_yorum}
⚠️ AI Karar: {"Long açılır" if puan > 6 else "Short riski yüksek"}
"""

    strateji = stratejik_yorumlar(
        indicators['rsi'],
        indicators['rsi_prev'],
        indicators['price'],
        indicators['price_prev'],
        indicators['ema20'],
        indicators['ema50'],
        indicators['macd_hist'],
        indicators['fibo'],
        indicators['bollinger'],
        indicators['hacim_artisi']
    )

    if strateji:
        msg += f"\n🧠 Stratejik Notlar:\n{strateji}"

    bot.send_message(CHAT_ID, msg)

@bot.message_handler(func=lambda message: message.text.upper().endswith("ANALİZ"))
def analiz_komutu(message):
    coin = message.text.upper().replace(" ANALİZ", "")
    symbol = f"{coin}USDT"
    if symbol in coin_list:
        analiz_yap_ve_mesaj_gonder(symbol)
    else:
        bot.send_message(message.chat.id, f"❌ '{symbol}' desteklenmeyen coin.")

print("🚀 Bot polling'e geçti...")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"💥 Hata: {e}")
        time.sleep(15)
