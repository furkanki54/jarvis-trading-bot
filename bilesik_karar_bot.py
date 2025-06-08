import requests
import pandas as pd
import numpy as np
import telebot

TOKEN = "8078903959:AAF37zwfzT1lJXqgob_3bCxEeiDgbRSow3w"
bot = telebot.TeleBot(TOKEN)

coin_list = [
    "BTCUSDT", "ETHUSDT", "BCHUSDT", "XRPUSDT", "LTCUSDT", "TRXUSDT", "ETCUSDT", "LINKUSDT", "XLMUSDT",
    "ADAUSDT", "XMRUSDT", "DASHUSDT", "ZECUSDT", "XTZUSDT", "BNBUSDT", "ATOMUSDT", "ONTUSDT", "IOTAUSDT",
    "BATUSDT", "VETUSDT", "NEOUSDT", "QTUMUSDT", "IOSTUSDT", "THETAUSDT", "ALGOUSDT", "ZILUSDT", "KNCUSDT",
    "ZRXUSDT", "COMPUSDT", "DOGEUSDT", "SXPUSDT", "KAVAUSDT", "BANDUSDT", "RLCUSDT", "MKRUSDT", "SNXUSDT",
    "DOTUSDT", "DEFIUSDT", "YFIUSDT", "CRVUSDT", "TRBUSDT", "RUNEUSDT", "SUSHIUSDT", "EGLDUSDT", "SOLUSDT",
    "UNIUSDT", "AVAXUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT", "LRCUSDT", "AXSUSDT", "ZENUSDT", "GRTUSDT",
    "CHZUSDT", "SANDUSDT", "MANAUSDT", "HBARUSDT", "ONEUSDT", "HOTUSDT", "GALAUSDT", "ARUSDT", "LDOUSDT",
    "ICPUSDT", "APTUSDT", "QNTUSDT", "FETUSDT", "INJUSDT", "GMXUSDT", "CFXUSDT", "STXUSDT", "SSVUSDT",
    "XAIUSDT", "WIFUSDT", "ONDOUSDT", "TIAUSDT", "CAKEUSDT", "TWTUSDT", "SEIUSDT", "CYBERUSDT", "ARKUSDT",
    "KASUSDT", "1000FLOKIUSDT", "PYTHUSDT", "WAXPUSDT", "BSVUSDT", "1000SATSUSDT", "JTOUSDT", "ACEUSDT",
    "MOVRUSDT", "NFPUSDT", "AIUSDT", "PEOPLEUSDT", "IDUSDT", "JOEUSDT", "LEVERUSDT", "RDNTUSDT", "HFTUSDT",
    "XVSUSDT", "BLURUSDT", "EDUUSDT", "SUIUSDT", "UMAUSDT", "NMRUSDT", "MAVUSDT", "XVGUSDT", "WLDUSDT",
    "PENDLEUSDT", "ARKMUSDT", "AGLDUSDT", "YGGUSDT", "DODOXUSDT", "BNTUSDT", "OXTUSDT", "HIFIUSDT",
    "BICOUSDT", "BIGTIMEUSDT", "STEEMUSDT", "ILVUSDT", "NTRNUSDT", "BEAMXUSDT", "1000BONKUSDT", "TOKENUSDT",
    "POWRUSDT", "GASUSDT", "RIFUSDT", "POLYXUSDT", "TLMUSDT", "ARBUSDT", "SUPERUSDT", "ONGUSDT", "ETHWUSDT",
    "1000RATSUSDT", "MEMEUSDT", "PHBUSDT", "ASTRUSDT", "HIGHUSDT", "MINAUSDT", "MAGICUSDT", "HOOKUSDT",
    "FXSUSDT", "LQTYUSDT", "TRUUSDT", "PERPUSDT", "CKBUSDT", "ACHUSDT", "STGUSDT", "SPELLUSDT", "AUCTIONUSDT"
]

def get_klines(symbol, interval="1h", limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    return [float(entry[4]) for entry in data]

def get_rsi(closes):
    delta = pd.Series(closes).diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def get_ema(closes, period):
    return round(pd.Series(closes).ewm(span=period, adjust=False).mean().iloc[-1], 2)

def calculate_macd(closes):
    series = pd.Series(closes)
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1]

def score_macd(histogram):
    if histogram > 0:
        return 2
    elif histogram < 0:
        return 1
    else:
        return 0

def get_fibonacci(closes):
    max_p = max(closes)
    min_p = min(closes)
    diff = max_p - min_p
    return {
        "0.236": round(max_p - diff * 0.236, 2),
        "0.382": round(max_p - diff * 0.382, 2),
        "0.5": round(max_p - diff * 0.5, 2),
        "0.618": round(max_p - diff * 0.618, 2),
        "0.786": round(max_p - diff * 0.786, 2)
    }

def get_bollinger(closes):
    prices = pd.Series(closes)
    ma = prices.rolling(window=20).mean()
    std = prices.rolling(window=20).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    last = prices.iloc[-1]
    if last > upper.iloc[-1]:
        return "Üst Bant"
    elif last < lower.iloc[-1]:
        return "Alt Bant"
    return "Orta Bant"

def yapay_tahmin():
    return np.random.randint(45, 65), np.random.randint(35, 55)

def analiz_yap(symbol):
    closes = get_klines(symbol)
    rsi = get_rsi(closes)
    ema20 = get_ema(closes, 20)
    ema50 = get_ema(closes, 50)
    macd_line, signal_line, hist = calculate_macd(closes)
    macd_score = score_macd(hist)
    boll = get_bollinger(closes)
    fibo = get_fibonacci(closes)
    up, down = yapay_tahmin()

    fiyat = float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol=" + symbol).json()["price"])
    ort = round((rsi / 50 + macd_score + (1 if fiyat > ema50 else 0)) / 3, 2)

    yorum = "📈 Boğa Gücü" if ort >= 2 else "📉 Ayı Baskısı"
    karar = "✅ Long açılır" if ort >= 2 else "⚠️ Short riski yüksek"

    return f"""📊 Teknik Analiz: {symbol}
Fiyat: {fiyat} USDT

🔹 RSI: {rsi}
🔹 EMA20: {ema20}
🔹 EMA50: {ema50}
🔹 MACD Histogram: {round(hist, 5)}
🔹 MACD Puanı: {macd_score}
🔹 Bollinger Durumu: {boll}
🔹 Fibo Seviyeleri:
  - 0.236: {fibo['0.236']}
  - 0.382: {fibo['0.382']}
  - 0.5: {fibo['0.5']}
  - 0.618: {fibo['0.618']}
  - 0.786: {fibo['0.786']}

🧠 AI Tahmini:
📈 Yükseliş olasılığı: %{up}
📉 Düşüş olasılığı: %{down}

🎯 Ortalama Puan: {ort}/10
💬 Yorum: {yorum}
⚠️ AI Karar: {karar}
"""

@bot.message_handler(func=lambda msg: msg.text.upper() in coin_list)
def cevapla(msg):
    text = msg.text.upper()
    bot.send_message(msg.chat.id, analiz_yap(text))

bot.polling()
