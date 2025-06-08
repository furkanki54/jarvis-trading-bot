import pandas as pd
import numpy as np
import requests
from telebot import TeleBot

TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
bot = TeleBot(TOKEN)

coin_list = [ "BTCUSDT", "ETHUSDT", "BCHUSDT", "XRPUSDT", "LTCUSDT", "TRXUSDT", "ETCUSDT", "LINKUSDT", "XLMUSDT",
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
"BOMEUSDT" ]

def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100"
    data = requests.get(url).json()
    return [float(i[4]) for i in data]

def calculate_rsi(prices, period=14):
    delta = np.diff(prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2) if not rsi.isna().all() else 50

def calculate_macd(prices):
    prices = pd.Series(prices)
    ema12 = prices.ewm(span=12, adjust=False).mean()
    ema26 = prices.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    hist = macd_line - signal_line
    scores = []

    for h in hist[-5:]:
        if h > 0:
            scores.append(2)
        elif h < 0:
            scores.append(0)
        else:
            scores.append(1)

    return scores

def calculate_bollinger(prices, period=20):
    series = pd.Series(prices)
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return lower.iloc[-1], sma.iloc[-1], upper.iloc[-1]

def calculate_fibonacci(prices):
    high = max(prices)
    low = min(prices)
    diff = high - low
    return {
        "0.236": round(high - 0.236 * diff, 2),
        "0.382": round(high - 0.382 * diff, 2),
        "0.5": round(high - 0.5 * diff, 2),
        "0.618": round(high - 0.618 * diff, 2),
        "0.786": round(high - 0.786 * diff, 2),
    }

def predict_trend(prices):
    trend = (prices[-1] - prices[-20]) / prices[-20]
    if trend > 0.02:
        return 75, 25
    elif trend < -0.02:
        return 25, 75
    else:
        return 50, 50

@bot.message_handler(func=lambda m: "analiz" in m.text.lower())
def analiz_et(m):
    try:
        symbol = m.text.split()[0].upper()
        if symbol not in coin_list:
            bot.send_message(m.chat.id, f"❌ {symbol} analiz listesinde yok.")
            return

        prices = get_klines(symbol)
        rsi = calculate_rsi(prices)
        ema20 = round(pd.Series(prices).ewm(span=20).mean().iloc[-1], 2)
        ema50 = round(pd.Series(prices).ewm(span=50).mean().iloc[-1], 2)
        macd_scores = calculate_macd(prices)
        price = prices[-1]
        lower, mid, upper = calculate_bollinger(prices)
        boll_pos = "Alt banda yakın" if price < lower else "Üst banda yakın" if price > upper else "Orta bant"
        fibo = calculate_fibonacci(prices)
        rise, fall = predict_trend(prices)
        fibo_text = "\n  - ".join([f"{k}: {v}" for k, v in fibo.items()])
        macd_avg = sum(macd_scores) / len(macd_scores)
        total_score = round((rsi / 100 * 3) + macd_avg + (1 if price > ema20 and price > ema50 else 0), 2)

        if total_score > 7:
            karar = "📈 AI Karar: Long açılır"
            yorum = "📈 Boğa Gücü"
        elif total_score > 4:
            karar = "⏳ AI Karar: Fırsat beklenmeli"
            yorum = "⚠️ Nötr"
        else:
            karar = "⚠️ AI Karar: Short riski yüksek"
            yorum = "📉 Ayı Baskısı"

        bot.send_message(m.chat.id, f"""
📊 Teknik Analiz: {symbol}
Fiyat: {price} USDT

🔹 RSI: {rsi}
🔹 EMA20: {ema20}
🔹 EMA50: {ema50}
🔹 MACD Puanları: {macd_scores}
🔹 Bollinger Durumu: {boll_pos}
🔹 Fibo Seviyeleri:
  - {fibo_text}

🧠 AI Tahmini:
📈 Yükseliş olasılığı: %{rise}
📉 Düşüş olasılığı: %{fall}

🎯 Ortalama Puan: {total_score}/10
💬 Yorum: {yorum}
{karar}
""")
    except Exception as e:
        bot.send_message(m.chat.id, f"Hata oluştu: {e}")

print("Bileşik Karar Botu çalışıyor...")
bot.polling()
