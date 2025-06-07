import asyncio
import aiohttp
import numpy as np
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import ta

TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
CHAT_ID = "-1002549376225"

TIMEFRAMES = {
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "1w": "1w"
}

HEADERS = {'User-Agent': 'Mozilla/5.0'}

async def get_ohlcv(symbol, interval, limit=100):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as resp:
            data = await resp.json()
            df = pd.DataFrame(data, columns=['time','open','high','low','close','volume','close_time',
                                             'quote_asset_volume','num_trades','taker_buy_base','taker_buy_quote','ignore'])
            df['close'] = df['close'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['volume'] = df['volume'].astype(float)
            return df

def load_coin_list():
    with open("coin_list.txt") as f:
        return [line.strip().upper() for line in f.readlines()]

def interpret(coin, price, signals):
    avg_rsi = np.mean(signals['rsi'])
    avg_macd = np.mean(signals['macd'])
    avg_ema = np.mean(signals['ema'])
    total_score = round((avg_rsi + avg_macd + avg_ema) / 3, 2)

    # Yorum ve sinyal
    if total_score >= 7:
        signal = "📈 Long sinyali"
        strategy = "Giriş fırsatı olabilir."
    elif total_score <= 3:
        signal = "📉 Short riski"
        strategy = "Düşüş baskısı yüksek."
    else:
        signal = "⚖️ Kararsız piyasa"
        strategy = "Net sinyal yok, izlenmeli."

    # Bollinger Yorumu
    boll_note = signals.get("boll", "")

    # Fibonacci Seviyeleri
    fibo = signals.get("fibo", [])
    fibo_note = f"🔹 Fibonacci: Önemli seviyeler: {', '.join([str(round(x,2)) for x in fibo])}"

    # Destek ve Direnç Yorumu
    support_note = signals.get("support", "")

    return f"""📊 Bileşik Teknik Analiz: {coin}
Fiyat: {price} USDT

🔹 RSI Puanları: {signals['rsi']}
🔹 MACD Puanları: {signals['macd']}
🔹 EMA Puanları: {signals['ema']}

{boll_note}
{fibo_note}
{support_note}

🎯 Ortalama Puan: {total_score}/10
💬 Yorum: {signal}
📌 Strateji: {strategy}
"""

async def analyze_coin(coin):
    signals = {"rsi": [], "macd": [], "ema": []}
    last_close = 0
    fib_levels = []
    for label, tf in TIMEFRAMES.items():
        df = await get_ohlcv(coin, tf)
        if df is None or df.empty:
            continue
        close = df['close']
        last_close = close.iloc[-1]
        
        # RSI
        rsi_val = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
        rsi_score = 3 if rsi_val < 30 else (2 if rsi_val < 50 else (1 if rsi_val < 70 else 0))
        signals['rsi'].append(rsi_score)

        # MACD
        macd = ta.trend.MACD(close)
        macd_hist = macd.macd_diff().iloc[-1]
        macd_score = 3 if macd_hist > 1 else (2 if macd_hist > 0 else (1 if macd_hist > -1 else 0))
        signals['macd'].append(macd_score)

        # EMA
        ema_fast = ta.trend.EMAIndicator(close, window=9).ema_indicator().iloc[-1]
        ema_slow = ta.trend.EMAIndicator(close, window=21).ema_indicator().iloc[-1]
        ema_score = 3 if ema_fast > ema_slow and last_close > ema_fast else (2 if last_close > ema_slow else 1)
        signals['ema'].append(ema_score)

        # Fibonacci (sadece 1D ile yapalım)
        if label == "1d":
            high = df['high'].max()
            low = df['low'].min()
            diff = high - low
            fib_levels = [high - diff * ratio for ratio in [0.236, 0.382, 0.5, 0.618, 0.786]]
            signals["fibo"] = fib_levels

        # Bollinger
        if label == "1h":
            bb = ta.volatility.BollingerBands(close)
            band_pos = close.iloc[-1] - bb.bollinger_mavg().iloc[-1]
            if band_pos > bb.bollinger_hband().iloc[-1]:
                signals["boll"] = "📍 Bollinger Pozisyonu: Üst Bant (Aşırı Alım)"
            elif band_pos < bb.bollinger_lband().iloc[-1]:
                signals["boll"] = "📍 Bollinger Pozisyonu: Alt Bant (Aşırı Satım)"
            else:
                signals["boll"] = "📍 Bollinger Pozisyonu: Orta Bant"

        # Destek/Direnç
        if label == "1d":
            support = fib_levels[2] if len(fib_levels) > 2 else low
            if last_close < support:
                signals["support"] = f"📉 {support} altına sarkarsa düşüş derinleşebilir."
            else:
                signals["support"] = f"📈 {support} üzerinde kalırsa güçlenebilir."

    return interpret(coin, round(last_close, 2), signals)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    if text.endswith("ANALIZ"):
        coin_symbol = text.replace("ANALIZ", "").strip()
        full_symbol = f"{coin_symbol}USDT"
        if full_symbol in load_coin_list():
            msg = await analyze_coin(full_symbol)
            await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("Bot hazır patron.")
    app.run_polling()
