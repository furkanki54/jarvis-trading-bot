# ai_predictor.py

import random

def predict_price_movement(rsi_values, macd_values, ema_values, volume_changes, price_changes):
    """
    Basit yapay zeka simülasyonu: RSI, MACD, EMA, hacim ve fiyat verilerine göre
    olasılık tahmini yapar.
    """

    # Ağırlıklı skor hesaplama (her indikatöre puan atıyoruz)
    score = 0

    # RSI değerlendirmesi
    for rsi in rsi_values:
        if rsi < 30:
            score += 1.5  # Aşırı satım → pozitif
        elif rsi > 70:
            score -= 1.5  # Aşırı alım → negatif
        else:
            score += 0.5  # Nötr

    # MACD değerlendirmesi
    for macd in macd_values:
        if macd > 0:
            score += 1
        else:
            score -= 1

    # EMA değerlendirmesi
    for ema in ema_values:
        if ema > 0:
            score += 1
        else:
            score -= 1

    # Hacim ve fiyat momentum
    if volume_changes[-1] > 0 and price_changes[-1] > 0:
        score += 1.5  # Momentum artışı

    # Normalize edip tahmin üret
    confidence = min(100, max(0, int(50 + score * 5)))
    direction = "YÜKSELİŞ" if score > 1 else "DÜŞÜŞ" if score < -1 else "YATAY"

    comment = f"""
🧠 AI Tahmini:
📊 Yön: {direction}
📈 Güven: %{confidence}

💡 Strateji:
"""
    if direction == "YÜKSELİŞ":
        comment += "Kısa vadeli long fırsatları değerlendirilebilir."
    elif direction == "DÜŞÜŞ":
        comment += "Short riski artıyor, dikkatli olunmalı."
    else:
        comment += "Net sinyal yok, yön belirginleşene kadar beklenmeli."

    return comment.strip()
