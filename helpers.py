import requests
from datetime import datetime

def get_technical_indicators(symbol: str, interval: str):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    response = requests.get(url)
    if response.status_code != 200:
        return {}

    data = response.json()
    closes = [float(item[4]) for item in data]
    if len(closes) < 50:
        return {}

    price = closes[-1]

    def calculate_rsi(data, period=14):
        gains = []
        losses = []
        for i in range(1, period + 1):
            delta = data[-i] - data[-i - 1]
            if delta >= 0:
                gains.append(delta)
            else:
                losses.append(abs(delta))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    rsi = calculate_rsi(closes)

    def ema(data, period):
        k = 2 / (period + 1)
        ema_val = sum(data[-period:]) / period
        for price in data[-period+1:]:
            ema_val = price * k + ema_val * (1 - k)
        return ema_val

    ema50 = ema(closes, 50)
    ema100 = ema(closes, 100)
    ema200 = ema(closes, 200) if len(closes) >= 200 else None

    def macd_calc(data):
        ema12 = ema(data, 12)
        ema26 = ema(data, 26)
        macd_val = ema12 - ema26
        signal = ema([ema12 - ema26 for _ in range(9)], 9)
        return macd_val, signal

    macd_val, macd_signal = macd_calc(closes)

    return {
        "rsi": round(rsi, 2),
        "macd": round(macd_val, 2),
        "macd_signal": round(macd_signal, 2),
        "ema50": round(ema50, 2),
        "ema100": round(ema100, 2),
        "ema200": round(ema200, 2) if ema200 else None,
        "price": round(price, 2)
    }

def analyze_coin(coin_symbol):
    timeframes = {
        "15 Dakika": "15m",
        "1 Saat": "1h",
        "4 Saat": "4h",
        "Günlük": "1d"
    }

    scores = {}
    details = {}
    current_price = None

    for label, tf in timeframes.items():
        indicators = get_technical_indicators(coin_symbol, tf)
        rsi = indicators.get("rsi")
        macd = indicators.get("macd")
        macd_signal = indicators.get("macd_signal")
        ema50 = indicators.get("ema50")
        ema100 = indicators.get("ema100")
        ema200 = indicators.get("ema200")
        current_price = indicators.get("price")  # Tüm zaman dilimlerinde aynı

        score = 0
        comment = []

        # RSI değerlendirme
        if rsi:
            if rsi < 30:
                comment.append("RSI çok düşük (aşırı satım)")
                score += 1
            elif 30 <= rsi <= 50:
                comment.append("RSI nötr-altı")
                score += 2
            elif 50 < rsi <= 70:
                comment.append("RSI pozitif bölgede")
                score += 3
            elif rsi > 70:
                comment.append("RSI çok yüksek (aşırı alım)")
                score += 2

        # MACD değerlendirme
        if macd and macd_signal:
            if macd > macd_signal:
                comment.append("MACD al sinyali")
                score += 3
            else:
                comment.append("MACD sat sinyali")
                score += 1

        # EMA değerlendirme
        if ema50 and ema100 and ema200 and current_price:
            if ema50 > ema100 > ema200 and current_price > ema50:
                comment.append("EMA yapısı güçlü boğa")
                score += 4
            elif ema50 < ema100 < ema200 and current_price < ema50:
                comment.append("EMA yapısı zayıf ayı")
                score += 1
            else:
                comment.append("EMA karışık, net yön yok")
                score += 2

        scores[label] = score
        details[label] = comment

    avg_score = sum(scores.values()) / len(scores)

    if avg_score >= 9:
        genel_sinyal = "🚀 Süper Boğa"
    elif avg_score >= 7:
        genel_sinyal = "📈 Güçlü Boğa"
    elif avg_score >= 5:
        genel_sinyal = "📊 Nötr / Hafif Boğa"
    elif avg_score >= 3:
        genel_sinyal = "⚠️ Ayı"
    else:
        genel_sinyal = "🐻 Güçlü Ayı"

    # Mesaj formatı
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"📊 {coin_symbol.upper()} Teknik Analiz – {now}\n"
    msg += f"💰 Güncel Fiyat: ${current_price:.2f}\n\n"

    for tf_label, score in scores.items():
        tf_sinyal = "Boğa" if score >= 6 else "Ayı" if score <= 4 else "Nötr"
        msg += f"⏱ {tf_label} → {tf_sinyal} ({score}/10)\n"
        for item in details[tf_label]:
            msg += f"    • {item}\n"
        msg += "\n"

    msg += f"🔎 Ortalama Boğa/Ayı Skoru: {avg_score:.2f}/10\n"
    msg += f"\n💬 Genel Yorum: {genel_sinyal}"

    return msg
