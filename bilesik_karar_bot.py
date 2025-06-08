import pandas as pd
import numpy as np
import requests
from telebot import TeleBot

TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
bot = TeleBot(TOKEN)

coin_list = [  # SENİN TAM LİSTEN
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

def get_klines(symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    return [float(entry[4]) for entry in data]

def calculate_macd(prices):
    prices = np.array(prices)
    ema12 = pd.Series(prices).ewm(span=12, adjust=False).mean()
    ema26 = pd.Series(prices).ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    scores = []
    for value in macd_hist[-5:]:
        if value > 0.0001:
            scores.append(2)
        elif value < -0.0001:
            scores.append(0)
        else:
            scores.append(1)
    return scores

@bot.message_handler(func=lambda message: "analiz" in message.text.lower())
def analyze(message):
    try:
        symbol = message.text.split()[0].upper()
        if symbol not in coin_list:
            bot.send_message(message.chat.id, f"⚠️ {symbol} analiz listesinde değil.")
            return

        prices = get_klines(symbol)
        rsi = round(np.mean(prices[-14:]), 2)
        ema20 = round(pd.Series(prices).ewm(span=20).mean().iloc[-1], 2)
        ema50 = round(pd.Series(prices).ewm(span=50).mean().iloc[-1], 2)
        macd_scores = calculate_macd(prices)
        macd_avg = sum(macd_scores) / len(macd_scores)
        price = prices[-1]

        total_score = round((rsi / 100 * 3) + macd_avg + (1 if price > ema20 and price > ema50 else 0), 2)

        if total_score > 7:
            karar = "📈 AI Karar: Long açılır"
        elif total_score > 5:
            karar = "✅ AI Karar: Short denenmez"
        elif total_score > 3:
            karar = "⏳ AI Karar: Fırsat için beklenmeli"
        else:
            karar = "⚠️ AI Karar: Short riski yüksek"

        yorum = "📈 Boğa Gücü" if total_score > 7 else "⚠️ Nötr" if total_score > 4 else "📉 Ayı Baskısı"

        bot.send_message(message.chat.id, f'''
📊 Teknik Analiz: {symbol}
Fiyat: {price} USDT

🔹 RSI: {rsi}
🔹 EMA20: {ema20}
🔹 EMA50: {ema50}
🔹 MACD Puanları: {macd_scores}

🎯 Ortalama Puan: {total_score}/10
💬 Yorum: {yorum}
{karar}
        ''')
    except Exception as e:
        bot.send_message(message.chat.id, f"Hata: {e}")

print("Bileşik Karar Botu çalışıyor...")
bot.polling()
