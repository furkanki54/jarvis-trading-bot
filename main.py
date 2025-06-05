import time
import requests
from telebot import TeleBot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, BINANCE_API_BASE, COIN_LIST_FILE
from utils import (
    get_binance_data,
    calculate_rsi,
    calculate_macd,
    calculate_ema,
    load_coin_list,
    detect_golden_cross,
    detect_death_cross
)

bot = TeleBot(TELEGRAM_TOKEN)
coin_list = load_coin_list(COIN_LIST_FILE)

VOLUME_THRESHOLD = 50  # %50 hacim artışı
PRICE_THRESHOLD = 3    # %3 fiyat değişimi
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

def analyze_coin(symbol):
    message_lines = []
    intervals = ["15m", "1h", "4h"]

    for interval in intervals:
        try:
            data = get_binance_data(symbol, interval)
            closes = [float(candle[4]) for candle in data]
            rsi = calculate_rsi(closes)
            macd_line, signal_line = calculate_macd(closes)
            ema50 = calculate_ema(closes, 50)
            ema200 = calculate_ema(closes, 200)

            # RSI yorumu
            rsi_msg = f"RSI({interval}): {rsi:.2f}"
            if rsi >= RSI_OVERBOUGHT:
                rsi_msg += " 🔴 Aşırı Alım"
            elif rsi <= RSI_OVERSOLD:
                rsi_msg += " 🟢 Aşırı Satım"
            message_lines.append(rsi_msg)

            # MACD yorumu
            macd_msg = f"MACD({interval}): {'🟢 Al Sinyali' if macd_line > signal_line else '🔴 Sat Sinyali'}"
            message_lines.append(macd_msg)

            # Golden/Death Cross
            if detect_golden_cross(ema50, ema200):
                message_lines.append(f"Golden Cross ({interval}) 🔔")
            elif detect_death_cross(ema50, ema200):
                message_lines.append(f"Death Cross ({interval}) ⚠️")

        except Exception as e:
            message_lines.append(f"{interval} verileri alınamadı: {str(e)}")

    return "\n".join(message_lines)

def send_alert(symbol, price_change, volume_change):
    message = (
        f"🚨 Hacim & Fiyat Alarmı: {symbol}\n"
        f"Fiyat Değişimi: %{price_change:.2f}\n"
        f"Hacim Değişimi: %{volume_change:.2f}"
    )
    bot.send_message(TELEGRAM_CHAT_ID, message)

def monitor():
    cache = {}
    while True:
        for symbol in coin_list:
            try:
                data = get_binance_data(symbol, "15m")
                current_close = float(data[-1][4])
                current_volume = float(data[-1][5])

                prev_close = float(data[-2][4])
                prev_volume = float(data[-2][5])

                price_change = ((current_close - prev_close) / prev_close) * 100
                volume_change = ((current_volume - prev_volume) / prev_volume) * 100

                if abs(price_change) >= PRICE_THRESHOLD and volume_change >= VOLUME_THRESHOLD:
                    send_alert(symbol, price_change, volume_change)

            except Exception as e:
                print(f"{symbol} için hata: {str(e)}")
        time.sleep(60)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip().upper()
    if text in coin_list:
        result = analyze_coin(text)
        bot.reply_to(message, f"📊 {text} Teknik Analiz:\n\n{result}")
    else:
        bot.reply_to(message, "Coin listesinde yok veya yanlış yazıldı.")

if __name__ == "__main__":
    monitor()
