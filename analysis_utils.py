from tech_indicators import get_rsi, get_macd, get_ema, get_bollinger_position, get_fibonacci_levels
from support_resistance import detect_support_resistance
from binance import Client
import os

client = Client()

def get_price(coin):
    ticker = client.get_symbol_ticker(symbol=coin)
    return float(ticker["price"])

def generate_decision(symbol):
    intervals = ["15m", "1h", "4h", "1d"]
    rsi_scores = []
    macd_scores = []
    ema_scores = []
    bollinger_notes = []
    
    for interval in intervals:
        rsi = get_rsi(symbol, interval)
        macd = get_macd(symbol, interval)
        ema = get_ema(symbol, interval)
        boll = get_bollinger_position(symbol, interval)

        rsi_scores.append(rsi)
        macd_scores.append(macd)
        ema_scores.append(ema)
        bollinger_notes.append(boll)

    price = get_price(symbol)
    support, resistance = detect_support_resistance(symbol, "1h")

    fibo = get_fibonacci_levels(symbol, "1d")

    decision = interpret(rsi_scores, macd_scores, ema_scores, bollinger_notes, price, support, resistance, fibo)

    return decision

def interpret(rsi, macd, ema, boll, price, support, resistance, fibo):
    score = sum(rsi + macd + ema) / (len(rsi + macd + ema) * 2) * 10
    score = round(score, 1)
    
    if score >= 7:
        signal = "🟢 Güçlü Long"
    elif score >= 5:
        signal = "🟡 Bekle, yön belirsiz"
    else:
        signal = "🔴 Short riski yüksek"

    fibo_note = f"🔹 Fibonacci: Önemli seviyeler: {', '.join([str(round(x,2)) for x in fibo])}"
    boll_note = f"📉 Bollinger Pozisyonu: {', '.join(boll)}"
    support_note = f"📌 Destek: {support} | Direnç: {resistance}"
    strategy = ""

    if price < support:
        strategy = f"⚠️ Fiyat {price} desteğin ({support}) altına indi. Short riski artabilir."
    elif price > resistance:
        strategy = f"📈 Fiyat {price} direncin ({resistance}) üzerine çıktı. Long fırsatı doğabilir."
    else:
        strategy = f"🧠 Fiyat {support} - {resistance} aralığında. Kırılım beklenmeli."

    return f"""📊 Teknik Analiz: {price} USDT

RSI: {rsi}
MACD: {macd}
EMA: {ema}

{boll_note}
{fibo_note}
{support_note}

🎯 Sinyal: {signal}
💬 Strateji: {strategy}
"""
