# bilesik_karar_bot.py
import time
import requests
import numpy as np
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
CHAT_ID = "-1002549376225"

coin_list = [  # 200+ coin gömülü liste
    "BTCUSDT", "ETHUSDT", "BCHUSDT", "XRPUSDT", "LTCUSDT", "TRXUSDT", "ETCUSDT", "LINKUSDT", "XLMUSDT",
    "ADAUSDT", "XMRUSDT", "DASHUSDT", "ZECUSDT", "XTZUSDT", "BNBUSDT", "ATOMUSDT", "ONTUSDT", "IOTAUSDT",
    "BATUSDT", "VETUSDT", "NEOUSDT", "QTUMUSDT", "IOSTUSDT", "THETAUSDT", "ALGOUSDT", "ZILUSDT", "KNCUSDT",
    "ZRXUSDT", "COMPUSDT", "DOGEUSDT", "SXPUSDT", "KAVAUSDT", "BANDUSDT", "RLCUSDT", "MKRUSDT", "SNXUSDT",
    "DOTUSDT", "DEFIUSDT", "YFIUSDT", "CRVUSDT", "TRBUSDT", "RUNEUSDT", "SUSHIUSDT", "EGLDUSDT", "SOLUSDT",
    "ICXUSDT", "STORJUSDT", "UNIUSDT", "AVAXUSDT", "ENJUSDT", "FLMUSDT", "KSMUSDT", "NEARUSDT", "AAVEUSDT",
    "FILUSDT", "RSRUSDT", "LRCUSDT", "BELUSDT", "AXSUSDT", "ALPHAUSDT", "ZENUSDT", "SKLUSDT", "GRTUSDT",
    "1INCHUSDT", "CHZUSDT", "SANDUSDT", "ANKRUSDT", "RVNUSDT", "SFPUSDT", "COTIUSDT", "CHRUSDT", "MANAUSDT",
    "ALICEUSDT", "HBARUSDT", "ONEUSDT", "DENTUSDT", "CELRUSDT", "HOTUSDT", "MTLUSDT", "OGNUSDT", "NKNUSDT",
    "1000SHIBUSDT", "BAKEUSDT", "GTCUSDT", "BTCDOMUSDT", "IOTXUSDT", "C98USDT", "MASKUSDT", "ATAUSDT",
    "DYDXUSDT", "1000XECUSDT", "GALAUSDT", "CELOUSDT", "ARUSDT", "ARPAUSDT", "CTSIUSDT", "LPTUSDT",
    "ENSUSDT", "PEOPLEUSDT", "ROSEUSDT", "DUSKUSDT", "FLOWUSDT", "IMXUSDT", "API3USDT", "GMTUSDT",
    "APEUSDT", "WOOUSDT", "JASMYUSDT", "OPUSDT", "INJUSDT", "STGUSDT", "SPELLUSDT", "1000LUNCUSDT",
    "LUNA2USDT", "LDOUSDT", "ICPUSDT", "APTUSDT", "QNTUSDT", "FETUSDT", "FXSUSDT", "HOOKUSDT", "MAGICUSDT",
    "TUSDT", "HIGHUSDT", "MINAUSDT", "ASTRUSDT", "PHBUSDT", "GMXUSDT", "CFXUSDT", "STXUSDT", "ACHUSDT",
    "SSVUSDT", "CKBUSDT", "PERPUSDT", "TRUUSDT", "LQTYUSDT", "IDUSDT", "ARBUSDT", "JOEUSDT", "TLMUSDT",
    "LEVERUSDT", "RDNTUSDT", "HFTUSDT", "XVSUSDT", "ETHBTC", "BLURUSDT", "EDUUSDT", "SUIUSDT", "1000FLOKIUSDT",
    "UMAUSDT", "NMRUSDT", "MAVUSDT", "XVGUSDT", "WLDUSDT", "PENDLEUSDT", "ARKMUSDT", "AGLDUSDT", "YGGUSDT",
    "DODOXUSDT", "BNTUSDT", "OXTUSDT", "SEIUSDT", "CYBERUSDT", "HIFIUSDT", "ARKUSDT", "BICOUSDT", "BIGTIMEUSDT",
    "WAXPUSDT", "BSVUSDT", "RIFUSDT", "POLYXUSDT", "GASUSDT", "POWRUSDT", "TIAUSDT", "CAKEUSDT", "MEMEUSDT",
    "TWTUSDT", "TOKENUSDT", "STEEMUSDT", "ILVUSDT", "NTRNUSDT", "KASUSDT", "BEAMXUSDT", "1000BONKUSDT",
    "PYTHUSDT", "SUPERUSDT", "ONGUSDT", "ETHWUSDT", "JTOUSDT", "1000SATSUSDT", "AUCTIONUSDT", "1000RATSUSDT",
    "ACEUSDT", "MOVRUSDT", "NFPUSDT", "AIUSDT", "XAIUSDT", "WIFUSDT", "MANTAUSDT", "ONDOUSDT", "POPCATUSDT",
    "BOMEUSDT"
]

def get_price(coin):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}"
    data = requests.get(url).json()
    return float(data["price"])

def get_klines(symbol, interval, limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    return [float(k[4]) for k in data], [float(k[5]) for k in data]

def calculate_rsi(prices):
    deltas = np.diff(prices)
    up = deltas[deltas > 0].sum()
    down = -deltas[deltas < 0].sum()
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices):
    prices = np.array(prices)

    ema12 = pd.Series(prices).ewm(span=12, adjust=False).mean()
    ema26 = pd.Series(prices).ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    # Son 5 histogram değerinden MACD puanı üret
    scores = []
    for value in histogram[-5:]:
        if value > 0.0001:
            scores.append(2)
        elif value < -0.0001:
            scores.append(0)
        else:
            scores.append(1)
    return scores

def calculate_ema(prices, period):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    return np.convolve(prices, weights, mode='valid')[-1]

def calculate_bollinger(prices):
    ma = np.mean(prices)
    std = np.std(prices)
    upper = ma + 2 * std
    lower = ma - 2 * std
    last = prices[-1]
    if last < lower:
        return "Alt Bant (Aşırı Satım)"
    elif last > upper:
        return "Üst Bant (Aşırı Alım)"
    else:
        return "Orta Bant"

def get_fibonacci_levels(prices):
    max_price = max(prices)
    min_price = min(prices)
    diff = max_price - min_price
    levels = [
        max_price - 0.236 * diff,
        max_price - 0.382 * diff,
        max_price - 0.5 * diff,
        max_price - 0.618 * diff,
        min_price
    ]
    return [round(level, 2) for level in levels]

def ai_prediction(rsi_scores, macd_scores, ema_scores):
    short_term = np.mean([rsi_scores[0], macd_scores[0], ema_scores[0]])
    mid_term = np.mean([rsi_scores[2], macd_scores[2], ema_scores[2]])
    return int(short_term * 10), int(mid_term * 10)

async def handle_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "analiz" not in text:
        return
    symbol = text.replace(" analiz", "").upper()
    if symbol not in coin_list:
        return

    fiyat = get_price(symbol)
    intervals = ["1m", "15m", "1h", "4h", "1d"]
    rsi_scores, macd_scores, ema_scores = [], [], []
    yorum = ""

    for interval in intervals:
        prices, _ = get_klines(symbol, interval)
        rsi = calculate_rsi(prices)
        rsi_scores.append(4 if rsi < 30 else 1 if rsi > 70 else 2)
        macd = calculate_macd(prices)
        macd_scores.append(3 if macd > 0 else 0)
        ema = calculate_ema(prices, 20)
        ema_scores.append(3 if prices[-1] > ema else 1)

    boll = calculate_bollinger(prices)
    fibo = get_fibonacci_levels(prices)
    avg_score = round(np.mean(rsi_scores + macd_scores + ema_scores), 2)

    if avg_score >= 7:
        yorum = "📈 Güçlü Boğa Sinyali"
    elif avg_score >= 4:
        yorum = "📊 Nötr / Belirsiz"
    else:
        yorum = "📉 Short Riski"

    st_pred, mt_pred = ai_prediction(rsi_scores, macd_scores, ema_scores)

    msg = f"""📊 Bileşik Teknik Analiz: {symbol}
Fiyat: {fiyat} USDT

🔹 RSI Puanları: {rsi_scores}
🔹 MACD Puanları: {macd_scores}
🔹 EMA Puanları: {ema_scores}

📍 Bollinger Pozisyonu: {boll}
🔹 Fibonacci: Önemli seviyeler: {', '.join([str(f) for f in fibo])}
📈 {fibo[2]} üzerinde kalırsa güçlenebilir.

🎯 Ortalama Puan: {avg_score}/10
💬 Yorum: {yorum}

🧠 AI Tahmini:
📈 1 saat içinde yükseliş olasılığı: %{st_pred}
📉 4 saat içinde düşüş riski: %{mt_pred}

💡 Strateji: RSI + EMA + MACD uyumu aranmalı.
"""
    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_analysis))
    print("Bot çalışıyor...")
    app.run_polling()
