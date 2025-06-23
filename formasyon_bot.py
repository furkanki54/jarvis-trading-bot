import requests
from telebot import TeleBot
import time

# Telegram ayarları
TELEGRAM_TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
CHAT_ID = "-1002549376225"
bot = TeleBot(TELEGRAM_TOKEN)

# Coin listesi
coin_list = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "LTCUSDT",
    "DOTUSDT", "LINKUSDT", "MATICUSDT", "OPUSDT", "ARBUSDT", "PEPEUSDT", "1000SHIBUSDT", "WIFUSDT", "SUIUSDT"
    # ... buraya senin tam 200+ coin listeni koyabilirsin
]

# Coin verilerini çekme
def fetch_data(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1h&limit=100"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data
    except:
        return None

# Basit formasyon kontrolü (örnek olarak çanak/kulp gibi)
def check_basic_pattern(data):
    if not data or len(data) < 3:
        return "Yeterli veri yok"
    lows = [float(candle[3]) for candle in data[-5:]]
    highs = [float(candle[2]) for candle in data[-5:]]
    if lows[0] > lows[2] < lows[4] and highs[0] < highs[2] < highs[4]:
        return "✅ Muhtemel TOBO formasyonu"
    elif lows[0] < lows[2] > lows[4] and highs[0] > highs[2] > highs[4]:
        return "⚠️ Olası OBO formasyonu"
    else:
        return "Formasyon tespit edilemedi"

# Formasyon analiz ve sinyal gönderme
def analiz_yap_ve_mesaj_gonder(symbol):
    data = fetch_data(symbol)
    formasyon = check_basic_pattern(data)
    current_price = float(data[-1][4]) if data else "?"
    message = f"""📉 Formasyon Analizi: {symbol}
Fiyat: {current_price} USDT
📌 Sonuç: {formasyon}"""
    bot.send_message(CHAT_ID, message)

# Telegram'dan mesajı yakala
@bot.message_handler(func=lambda message: message.text and message.text.upper().endswith("ANALİZ"))
def handle_analysis(message):
    coin = message.text.upper().replace(" ANALİZ", "")
    symbol = f"{coin}USDT"
    if symbol in coin_list:
        analiz_yap_ve_mesaj_gonder(symbol)
    else:
        bot.send_message(message.chat.id, f"❌ '{coin}' coini desteklenmiyor.")

# Botu başlat
print("Formasyon botu çalışıyor...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Hata: {e}")
        time.sleep(15)
