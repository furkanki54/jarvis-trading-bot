import time
import requests
from datetime import datetime
import telebot

# Telegram bot bilgileri
BOT_TOKEN = "7759276451:AAF0Xphio-TjtYyFIzahQrG3fU-qdNQuBEw"
CHAT_ID = "-1002549376225"
bot = telebot.TeleBot(BOT_TOKEN)

# Coin listesi dosyası
COIN_LIST_FILE = "coin_list_500_sample.txt"

def load_coin_list():
    with open(COIN_LIST_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def get_gecko_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=hourly"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def analyze_coin(coin_id):
    data = get_gecko_data(coin_id)
    if not data or 'prices' not in data:
        return None

    prices = [p[1] for p in data["prices"]]
    volumes = [v[1] for v in data["total_volumes"]]

    # Fiyat değişimi (yüzde olarak)
    change = (prices[-1] - prices[-2]) / prices[-2] * 100
    volume_change = (volumes[-1] - volumes[-2]) / volumes[-2] * 100 if volumes[-2] != 0 else 0

    # MACD hesaplama (basit)
    ema12 = sum(prices[-12:]) / 12
    ema26 = sum(prices[-26:]) / 26
    macd = ema12 - ema26
    signal_line = sum(prices[-9:]) / 9

    # RSI hesaplama (basit)
    gains = [max(prices[i + 1] - prices[i], 0) for i in range(13)]
    losses = [abs(min(prices[i + 1] - prices[i], 0)) for i in range(13)]
    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    trend = "Boğa" if rsi > 55 and macd > signal_line else "Ayı"

    if abs(change) >= 1 or abs(volume_change) >= 30:
        message = (
            f"📊 Coin: {coin_id}\n"
            f"💵 Fiyat değişimi (1s): {change:.2f}%\n"
            f"📈 Hacim değişimi (1s): {volume_change:.2f}%\n"
            f"📉 RSI: {rsi:.2f}\n"
            f"📊 MACD: {macd:.4f}\n"
            f"📊 Signal: {signal_line:.4f}\n"
            f"📣 Trend Yorumu: {trend} piyasası!"
        )
        return message
    return None

def main():
    coin_list = load_coin_list()
    while True:
        for coin in coin_list:
            try:
                result = analyze_coin(coin)
                if result:
                    bot.send_message(CHAT_ID, result)
            except Exception as e:
                print(f"Hata {coin}: {e}")
            time.sleep(1.5)
        print(f"Saatlik analiz tamamlandı: {datetime.now()}")
        time.sleep(3600)  # 1 saat uyku

if __name__ == "__main__":
    main()
