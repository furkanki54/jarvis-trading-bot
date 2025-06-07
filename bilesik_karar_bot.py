import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from binance.client import Client
from support_resistance import detect_support_resistance
import pandas as pd
import numpy as np
from config import TELEGRAM_TOKEN
import os

client = Client()

logging.basicConfig(level=logging.INFO)

def load_coin_list():
    with open("coin_list.txt", "r") as f:
        return [line.strip().upper() for line in f if line.strip()]

def get_ohlcv(symbol, interval="1h", limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    return df

def analyze_coin(symbol):
    df_1h = get_ohlcv(symbol, "1h")
    df_4h = get_ohlcv(symbol, "4h")
    df_1d = get_ohlcv(symbol, "1d")

    def get_scores(df):
        close = df['close']
        rsi = RSIIndicator(close).rsi()
        macd = MACD(close).macd_diff()
        ema_fast = EMAIndicator(close, window=12).ema_indicator()
        ema_slow = EMAIndicator(close, window=26).ema_indicator()

        rsi_score = 0
        if rsi.iloc[-1] < 30:
            rsi_score = 3
        elif rsi.iloc[-1] < 50:
            rsi_score = 2
        elif rsi.iloc[-1] < 70:
            rsi_score = 1

        macd_score = 0
        if macd.iloc[-1] > 0 and macd.iloc[-2] <= 0:
            macd_score = 3
        elif macd.iloc[-1] > 0:
            macd_score = 2
        elif macd.iloc[-1] > macd.iloc[-2]:
            macd_score = 1

        ema_score = 0
        if close.iloc[-1] > ema_fast.iloc[-1] > ema_slow.iloc[-1]:
            ema_score = 3
        elif close.iloc[-1] > ema_fast.iloc[-1]:
            ema_score = 2
        elif close.iloc[-1] > ema_slow.iloc[-1]:
            ema_score = 1

        return rsi_score, macd_score, ema_score

    rsi_scores = []
    macd_scores = []
    ema_scores = []

    for df in [df_1h, df_4h, df_1d]:
        rsi, macd, ema = get_scores(df)
        rsi_scores.append(rsi)
        macd_scores.append(macd)
        ema_scores.append(ema)

    avg_score = round(np.mean(rsi_scores + macd_scores + ema_scores), 2)

    yorum = "📈 Boğa gücü yüksek" if avg_score >= 7 else "📉 Ayı baskısı fazla" if avg_score <= 3 else "⚖️ Kararsız piyasa"

    price = df_1h['close'].iloc[-1]
    support, resistance = detect_support_resistance(symbol, interval="1h")

    destek_yorum = ""
    if price < support:
        destek_yorum = f"📉 Fiyat {support} desteğinin altına sarktı. Short baskısı artabilir."
    elif price > resistance:
        destek_yorum = f"📈 Fiyat {resistance} direncinin üzerine çıktı. Long baskısı artabilir."
    else:
        destek_yorum = f"🎯 Fiyat {support} – {resistance} aralığında."

    message = f"""📊 Bileşik Teknik Analiz: {symbol}
Fiyat: {price} USDT
🔹 RSI Puanları: {rsi_scores}
🔹 MACD Puanları: {macd_scores}
🔹 EMA Puanları: {ema_scores}
🎯 Ortalama Puan: {avg_score}/10
💬 Yorum: {yorum}
{destek_yorum}
"""

    return message

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    if text.endswith("ANALIZ"):
        coin_symbol = text.replace("ANALIZ", "").strip()
        if coin_symbol in load_coin_list():
            msg = analyze_coin(f"{coin_symbol}USDT")
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text(f"❌ '{coin_symbol}' listede bulunamadı.")
    else:
        await update.message.reply_text("📌 Format: COIN ANALIZ (örnek: BTC ANALIZ)")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot çalışıyor... Telegram'dan yazabilirsin.")
    app.run_polling()
