import requests
import time
import telebot

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_top_coins(limit=100):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    res = requests.get(url)
    data = res.json()
    usdt_pairs = [item['symbol'] for item in data if item['symbol'].endswith('USDT') and not item['symbol'].endswith('BUSDUSDT')]
    return usdt_pairs[:limit]

def get_5m_kline(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=6"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    return res.json()

def analyze_coin(symbol):
    klines = get_5m_kline(symbol)
    if len(klines) < 6:
        return None

    prev_5 = klines[-6:-1]
    last = klines[-1]

    prev_volumes = [float(k[5]) for k in prev_5]
    avg_prev_volume = sum(prev_volumes) / len(prev_volumes)
    last_volume = float(last[5])

    volume_change_pct = ((last_volume - avg_prev_volume) / avg_prev_volume) * 100

    open_price = float(last[1])
    close_price = float(last[4])
    price_change_pct = ((close_price - open_price) / open_price) * 100

    if volume_change_pct >= 30 and price_change_pct >= 2:
        return {
            "symbol": symbol,
            "volume_change": round(volume_change_pct, 2),
            "price_change": round(price_change_pct, 2),
            "price": round(close_price, 4)
        }
    return None

def send_alert(info):
    msg = f"""🐳 BALİNA ALIMI TESPİT EDİLDİ!
Coin: {info['symbol']}
Fiyat: ${info['price']}
Fiyat Artışı (5dk): %{info['price_change']}
Hacim Artışı: %{info['volume_change']}

Bu ani yükseliş büyük alım sinyali olabilir.
"""
    bot.send_message(TELEGRAM_CHAT_ID, msg)

def main_loop():
    already_alerted = set()
    while True:
        try:
            coin_list = get_top_coins(100)
            for coin in coin_list:
                result = analyze_coin(coin)
                if result and result['symbol'] not in already_alerted:
                    send_alert(result)
                    already_alerted.add(result['symbol'])

            time.sleep(300)  # 5 dakika bekle
        except Exception as e:
            print("Hata:", e)
            time.sleep(60)

if __name__ == "__main__":
    main_loop()
