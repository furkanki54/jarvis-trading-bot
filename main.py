import requests
import time
from telebot import TeleBot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils import get_binance_data, calculate_rsi, calculate_macd, calculate_ema, load_coin_list

bot = TeleBot(TELEGRAM_TOKEN)
coin_list = load_coin_list("coin_list_updated.txt")
VOLUME_THRESHOLD = 50  # Hacim değişimi eşiği (%)
PRICE_THRESHOLD = 3    # Fiyat değişimi eşiği (%)

def analyze_coin(symbol):
    try:
        df = get_binance_data(symbol)
        if df is None or df.empty:
            return None

        volume_change = ((df['volume'].iloc[-1] - df['volume'].iloc[-2]) / df['volume'].iloc[-2]) * 100
        price_change = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100

        rsi_value = calculate_rsi(df)
        ema_value = calculate_ema(df)
        macd_value = calculate_macd(df)

        rsi_status = "🔼 Boğa" if rsi_value > 50 else "🔽 Ayı"
        ema_status = "🔼 Boğa" if df['close'].iloc[-1] > ema_value else "🔽 Ayı"
        macd_status = "🔼 Boğa" if macd_value > 0 else "🔽 Ayı"

        boğa_puanı = sum([
            1 if rsi_status == "🔼 Boğa" else 0,
            1 if ema_status == "🔼 Boğa" else 0,
            1 if macd_status == "🔼 Boğa" else 0
        ])
        genel_yon = "Boğa" if boğa_puanı >= 2 else "Ayı"

        mesaj = f"""📉 BALİNA SİNYALİ!
🌕 Coin: {symbol.upper()}
💲 Fiyat Değişimi: %{price_change:.2f}
📊 Hacim Değişimi: %{volume_change:.2f}
{rsi_status} | {ema_status} | {macd_status}
🚀 Genel Yön: {genel_yon} (Boğa Puanı: {boğa_puanı}/3)"""

        return mesaj if volume_change > VOLUME_THRESHOLD and abs(price_change) > PRICE_THRESHOLD else None
    except Exception as e:
        return f"⚠️ Hata oluştu: {e}"

def hourly_scan():
    sinyal_var_mi = False
    for coin in coin_list:
        symbol = f"{coin.upper()}"
        sinyal = analyze_coin(symbol)
        if sinyal:
            bot.send_message(TELEGRAM_CHAT_ID, sinyal)
            sinyal_var_mi = True
    if not sinyal_var_mi:
        bot.send_message(TELEGRAM_CHAT_ID, "📡 Saatlik tarama tamamlandı, sinyale rastlanmadı.")

@bot.message_handler(func=lambda message: True)
def handle_user_msg(message):
    symbol = message.text.strip().upper()
    sinyal = analyze_coin(symbol)
    if sinyal:
        bot.send_message(message.chat.id, sinyal)
    else:
        bot.send_message(message.chat.id, "📡 Teknik analiz tamamlandı, sinyal yok.")

def start_polling():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    start_polling()
