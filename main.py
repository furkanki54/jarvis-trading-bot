from telebot import TeleBot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils import (
    load_coin_list,
    get_binance_data,
    calculate_rsi,
    calculate_macd,
    calculate_ema,
    analyze_indicators,
    analyze_price_volume,
)

bot = TeleBot(TELEGRAM_TOKEN)
coin_list = load_coin_list("coin_list_binance.txt")

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 Merhaba! Coin ismini yazarak analiz alabilirsin. (örn: BTCUSDT)")

@bot.message_handler(func=lambda message: True)
def handle_user_msg(message):
    symbol = message.text.strip().upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"

    if symbol not in coin_list:
        bot.send_message(message.chat.id, f"❌ {symbol} analiz listesinde bulunamadı.")
        return

    intervals = ["15m", "1h", "4h"]
    interval_names = {"15m": "15 Dakika", "1h": "1 Saat", "4h": "4 Saat"}
    responses = []

    for interval in intervals:
        df = get_binance_data(symbol, interval)
        if df is None or df.empty:
            continue

        rsi_status = calculate_rsi(df)
        macd_status = calculate_macd(df)
        ema_status = calculate_ema(df)
        boğa_puanı = [rsi_status, macd_status, ema_status].count("📈 Boğa")

        genel_yön = "📈 Boğa" if boğa_puanı >= 2 else "📉 Ayı"

        mesaj = (
            f"📊 *{symbol} - {interval_names[interval]}*\n"
            f"RSI: {rsi_status}\n"
            f"MACD: {macd_status}\n"
            f"EMA: {ema_status}\n"
            f"Genel Yön: {genel_yön} (Boğa Puanı: {boğa_puanı}/3)"
        )
        responses.append(mesaj)

    if responses:
        for m in responses:
            bot.send_message(message.chat.id, m, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"🔍 {symbol} için teknik analiz yapılamadı.")

bot.polling(non_stop=True)
