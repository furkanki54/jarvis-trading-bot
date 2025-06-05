import time
from telebot import TeleBot
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils import get_binance_data, calculate_rsi, calculate_macd, calculate_ema, load_coin_list

bot = TeleBot(TELEGRAM_TOKEN)
coin_list = load_coin_list("coin_list_binance.txt")

VOLUME_THRESHOLD = 50  # % hacim artışı eşiği
PRICE_THRESHOLD = 3    # % fiyat değişimi eşiği

def analyze_coin(symbol):
    try:
        df = get_binance_data(symbol)
        if df is None:
            return f"{symbol} için veri alınamadı."

        rsi = calculate_rsi(df)
        macd_hist = calculate_macd(df)
        ema_short, ema_long = calculate_ema(df)

        last_rsi = rsi.iloc[-1]
        last_macd = macd_hist.iloc[-1]
        signal = f"📊 Teknik analiz - {symbol}\n"

        if last_rsi > 70:
            signal += "🔴 RSI: Aşırı alım bölgesinde.\n"
        elif last_rsi < 30:
            signal += "🟢 RSI: Aşırı satım bölgesinde.\n"
        else:
            signal += f"RSI: {last_rsi:.2f}\n"

        if last_macd > 0:
            signal += "🟢 MACD: Al sinyali.\n"
        else:
            signal += "🔴 MACD: Sat sinyali.\n"

        if ema_short.iloc[-1] > ema_long.iloc[-1]:
            signal += "🟢 EMA: Golden Cross (Yükseliş).\n"
        else:
            signal += "🔴 EMA: Death Cross (Düşüş).\n"

        return signal
    except Exception as e:
        return f"{symbol} analizi başarısız: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    symbol = message.text.strip().upper()
    if symbol in coin_list:
        signal = analyze_coin(symbol)
        bot.send_message(TELEGRAM_CHAT_ID, signal)
    else:
        bot.send_message(TELEGRAM_CHAT_ID, f"❌ Coin '{symbol}' listede yok.")

while True:
    for symbol in coin_list:
        df = get_binance_data(symbol)
        if df is None:
            continue

        volume_now = df["volume"].iloc[-1]
        volume_prev = df["volume"].iloc[-2]
        price_now = df["close"].iloc[-1]
        price_prev = df["close"].iloc[-2]

        if volume_prev == 0:
            continue

        volume_change = ((volume_now - volume_prev) / volume_prev) * 100
        price_change = ((price_now - price_prev) / price_prev) * 100

        if volume_change > VOLUME_THRESHOLD and abs(price_change) > PRICE_THRESHOLD:
            signal = f"📈 {symbol} sinyali:\nHacim: %{volume_change:.2f}, Fiyat: %{price_change:.2f}"
            bot.send_message(TELEGRAM_CHAT_ID, signal)

    time.sleep(60)
