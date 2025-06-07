import pandas as pd
import numpy as np
import requests
from telebot import TeleBot

TOKEN = "8171630986:AAFUJ6tTJsAYDg6ZeOt0AyU43k3RjaKmfGc"
bot = TeleBot(TOKEN)

# 🔒 SADECE SEÇİLMİŞ COINLERLE ÇALIŞ
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

# ✅ DÜZELTİLMİŞ MACD HESABI
def calculate_macd(prices):
    try:
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
    except Exception as e:
        print(f"MACD hesaplama hatası: {e}")
        return [0, 0, 0, 0, 0]

# 🔁 BOT KOMUTLARI (ESKİDEN AYNI KALSIN)
@bot.message_handler(func=lambda message: "analiz" in message.text.lower())
def analyze_message(message):
    symbol = message.text.split()[0].upper()
    
    if symbol not in coin_list:
        bot.send_message(message.chat.id, f"⚠️ {symbol} analiz listesinde değil.")
        return

    # Eski analiz yapısı korunacak: RSI, EMA, MACD + AI karar sistemi
    # Kodun geri kalanı senin eski dosyandaki gibi devam eder...
    ...
    
bot.polling()
