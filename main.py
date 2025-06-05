import time
import logging
from telebot import TeleBot
from utils import (
    get_binance_data,
    calculate_rsi,
    calculate_macd,
    calculate_ema,
    load_coin_list,
    analyze_indicators,
    analyze_price_volume
)
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = TeleBot(TELEGRAM_TOKEN)
coin_list = load_coin_list("coin_list_binance.txt")

LAST_MESSAGE_TIME = 0

def safe_send_message(chat_id, text, parse_mode=None):
    global LAST_MESSAGE_TIME
    now = time.time()
    if now - LAST_MESSAGE_TIME >= 1.5:
        bot.send_message(chat_id, text, parse_mode=parse_mode)
        LAST_MESSAGE_TIME = now

def analyze_and_signal():
    for symbol in coin_list:
        try:
            df = get_binance_data(symbol)
            if df is None or df.empty:
                continue

            rsi = calculate_rsi(df)
            macd, _ = calculate_macd(df)
            ema = calculate_ema(df)

            indicator_msg = analyze_indicators(symbol, rsi, macd, ema)
            price_volume_msg = analyze_price_volume(symbol, df)

            if indicator_msg:
                safe_send_message(TELEGRAM_CHAT_ID, indicator_msg, parse_mode="Markdown")
            if price_volume_msg:
                safe_send_message(TELEGRAM_CHAT_ID, price_volume_msg, parse_mode="Markdown")

        except Exception as e:
            logging.error(f"Hata {symbol}: {e}")

@bot.message_handler(func=lambda message: True)
def handle_user_msg(message):
    symbol = message.text.strip().upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    if symbol not in coin_list:
        safe_send_message(message.chat.id, f"❌ {symbol} analiz listesinde bulunamadı.")
        return

    try:
        df = get_binance_data(symbol)
        if df is None or df.empty:
            safe_send_message(message.chat.id, f"❌ {symbol} için veri alınamadı.")
            return

        rsi = calculate_rsi(df)
        macd, _ = calculate_macd(df)
        ema = calculate_ema(df)

        indicator_msg = analyze_indicators(symbol, rsi, macd, ema)
        price_volume_msg = analyze_price_volume(symbol, df)

        if indicator_msg:
            safe_send_message(message.chat.id, indicator_msg, parse_mode="Markdown")
        if price_volume_msg:
            safe_send_message(message.chat.id, price_volume_msg, parse_mode="Markdown")
        if not indicator_msg and not price_volume_msg:
            safe_send_message(message.chat.id, "📉 Sinyale rastlanmadı.")

    except Exception as e:
        logging.error(f"Kullanıcı komutu hatası {symbol}: {e}")
        safe_send_message(message.chat.id, f"⚠️ Hata oluştu: {e}")

if __name__ == "__main__":
    analyze_and_signal()
    bot.polling(non_stop=True)
