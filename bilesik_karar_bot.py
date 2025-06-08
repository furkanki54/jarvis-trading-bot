import telebot
import requests
import pandas as pd
import numpy as np

TOKEN = "YENİ_TOKENIN_BURAYA"  # Buraya yeni tokenı gir
bot = telebot.TeleBot(TOKEN)

coin_list = [
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

def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    r = requests.get(url)
    return [float(i[4]) for i in r.json()]

def calculate_macd(closes):
    closes = pd.Series(closes)
    exp1 = closes.ewm(span=12, adjust=False).mean()
    exp2 = closes.ewm(span=26, adjust=False).mean()
    macd_line = exp1 - exp2
    signal = macd_line.ewm(span=9, adjust=False).mean()
    hist = macd_line - signal
    return macd_line.iloc[-1], signal.iloc[-1], hist.iloc[-1]

def get_ema(closes, period):
    return pd.Series(closes).ewm(span=period, adjust=False).mean().iloc[-1]

def get_rsi(closes):
    delta = pd.Series(closes).diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_bollinger(closes):
    series = pd.Series(closes)
    sma = series.rolling(window=20).mean()
    std = series.rolling(window=20).std()
    upper = sma + (std * 2)
    lower = sma - (std * 2)
    price = series.iloc[-1]
    if price > upper.iloc[-1]:
        return "Üst Bant"
    elif price < lower.iloc[-1]:
        return "Alt Bant"
    else:
        return "Orta Bant"

def fibonacci_levels(closes):
    max_price = max(closes)
    min_price = min(closes)
    diff = max_price - min_price
    levels = {
        "0.236": max_price - 0.236 * diff,
        "0.382": max_price - 0.382 * diff,
        "0.5": max_price - 0.5 * diff,
        "0.618": max_price - 0.618 * diff,
        "0.786": max_price - 0.786 * diff,
    }
    return levels

@bot.message_handler(func=lambda msg: msg.text.lower() == "btc analiz")
def analiz_yap(msg):
    symbol = "BTCUSDT"
    closes = get_klines(symbol)
    fiyat = closes[-1]
    rsi = get_rsi(closes)
    ema20 = get_ema(closes, 20)
    ema50 = get_ema(closes, 50)
    macd_line, signal_line, hist = calculate_macd(closes)
    bollinger = calculate_bollinger(closes)
    fibo = fibonacci_levels(closes)

    macd_score = 1 if macd_line > signal_line and hist > 0 else 0
    ort_puan = round((macd_score + (rsi / 100) + (fiyat > ema20) + (fiyat > ema50)) / 4 * 10, 2)
    yorum = "📈 Boğa Gücü" if ort_puan > 6 else "📉 Ayı Baskısı"

    mesaj = f"""📊 Teknik Analiz: {symbol}
Fiyat: {round(fiyat, 2)} USDT

🔹 RSI: {round(rsi, 2)}
🔹 EMA20: {round(ema20, 2)}
🔹 EMA50: {round(ema50, 2)}
🔹 MACD Histogram: {round(hist, 5)}
🔹 Bollinger Durumu: {bollinger}
🔹 Fibo Seviyeleri:\n""" + "\n".join([f"  - {k}: {round(v, 2)}" for k, v in fibo.items()]) + f"""

🎯 Ortalama Puan: {ort_puan}/10
💬 Yorum: {yorum}
⚠️ AI Karar: {'Long açılır' if ort_puan > 6 else 'Short riski yüksek'}
"""

    bot.send_message(msg.chat.id, mesaj)

bot.polling()
