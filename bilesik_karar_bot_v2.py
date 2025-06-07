import requests
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = "8078903959:AAF37zwfzT1lJXqgob_3bCxEeiDgbRSow3w"

def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data, columns=['time','open','high','low','close','volume','close_time',
                                       'qav','num_trades','taker_base_vol','taker_quote_vol','ignore']).astype(float)

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs.iloc[-1]))

def calculate_bollinger(prices, period=20):
    ma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    return upper.iloc[-1], ma.iloc[-1], lower.iloc[-1]

def calculate_fibonacci(prices):
    max_price = prices.max()
    min_price = prices.min()
    diff = max_price - min_price
    levels = {
        "0.236": max_price - diff * 0.236,
        "0.382": max_price - diff * 0.382,
        "0.5": max_price - diff * 0.5,
        "0.618": max_price - diff * 0.618,
        "0.786": max_price - diff * 0.786
    }
    return levels

def analyze(symbol="BTCUSDT"):
    timeframes = {"15m": "15 Dakika", "1h": "1 Saat", "4h": "4 Saat", "1d": "1 Gün"}
    rsi_data = {}
    summary = ""

    for tf in timeframes:
        df = get_klines(symbol, tf)
        prices = df["close"]
        rsi = round(calculate_rsi(prices), 2)
        rsi_data[tf] = rsi
        summary += f"{timeframes[tf]} RSI: {rsi}\n"

    df_daily = get_klines(symbol, "1d")
    prices_daily = df_daily["close"]
    last_price = round(prices_daily.iloc[-1], 2)
    upper, ma, lower = calculate_bollinger(prices_daily)
    fibo_levels = calculate_fibonacci(prices_daily)

    decision = ""
    if all(r > 70 for r in rsi_data.values()):
        decision = "RSI çok şişmiş. Aşırı alım bölgesinde. Long riskli, düzeltme gelebilir."
    elif all(r < 30 for r in rsi_data.values()):
        decision = "RSI çok düşük. Aşırı satımda. Long fırsatı oluşabilir."
    else:
        decision = "RSI kararsız. Fiyat izlenmeli."

    price_context = ""
    support = fibo_levels["0.5"]
    resistance = fibo_levels["0.236"]
    if last_price > resistance:
        price_context = f"📈 Fiyat {resistance} üzerinde. Eğer üzerinde tutunursa long denenebilir."
    elif last_price < support:
        price_context = f"📉 Fiyat {support} altına sarktı. Bu bölge altında short riski artar."
    else:
        price_context = f"⏳ Fiyat destek ({support}) ile direnç ({resistance}) arasında. Karar için net kırılım beklenmeli."

    text = f"📊 {symbol} Analizi\nFiyat: {last_price} USDT\n\n"
    text += summary
    text += f"\n🔍 Bollinger Bands:\nÜst: {round(upper,2)}\nOrta: {round(ma,2)}\nAlt: {round(lower,2)}"
    text += f"\n\n📐 Fibonacci Seviyeleri:\n"
    for k, v in fibo_levels.items():
        text += f"{k}: {round(v,2)}\n"
    text += f"\n🧠 Karar: {decision}\n{price_context}"

    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper()
    if "ANALİZ" in text:
        coin = text.replace("ANALİZ", "").strip().upper()
        if not coin.endswith("USDT"):
            coin += "USDT"
        result = analyze(coin)
        await update.message.reply_text(result)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
