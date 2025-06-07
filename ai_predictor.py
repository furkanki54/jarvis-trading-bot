# ai_predictor.py

def predict_price_movement(df, timeframe_label="1 Saat"):
    """
    df: pandas DataFrame (fiyat verisi)
    timeframe_label: zaman dilimi etiketi (örnek: "1 Saat", "4 Saat")

    Çıktı: detaylı tahmin metni (str)
    """

    if df is None or df.empty:
        return f"❗ {timeframe_label} verisi bulunamadı."

    close = df['close']
    if len(close) < 10:
        return f"❗ {timeframe_label} için yeterli veri yok."

    # RSI
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    rsi_score = 1.5 if rsi < 30 else (-1.5 if rsi > 70 else 0)

    # MACD
    macd_diff = ta.trend.MACD(close).macd_diff()
    macd_delta = macd_diff.iloc[-1] - macd_diff.iloc[-2]
    macd_score = 1 if macd_diff.iloc[-1] > 0 else -1
    macd_slope_score = 1 if macd_delta > 0 else -1

    # EMA
    ema_fast = ta.trend.EMAIndicator(close, window=9).ema_indicator().iloc[-1]
    ema_slow = ta.trend.EMAIndicator(close, window=21).ema_indicator().iloc[-1]
    ema_score = 1 if ema_fast > ema_slow else -1

    # Hacim (varsa)
    try:
        vol = df['volume']
        vol_change = (vol.iloc[-1] - vol.iloc[-2]) / vol.iloc[-2] * 100
        vol_score = 1 if vol_change > 0 else -1
    except:
        vol_score = 0

    # Toplam skor
    total_score = rsi_score + macd_score + macd_slope_score + ema_score + vol_score

    # Yorumlama
    direction = "YÜKSELİŞ" if total_score >= 2 else "DÜŞÜŞ" if total_score <= -2 else "YATAY"
    confidence = min(100, max(50, int(60 + total_score * 5)))

    # Strateji
    if direction == "YÜKSELİŞ":
        strategy = f"📈 {timeframe_label} için long fırsatı olabilir."
    elif direction == "DÜŞÜŞ":
        strategy = f"📉 {timeframe_label} için short riski artıyor."
    else:
        strategy = f"⚖️ {timeframe_label} için net sinyal yok."

    # Final mesaj
    return f"""
🧠 AI Tahmini ({timeframe_label}):
🔹 Yön: {direction}
🔹 Güven: %{confidence}
{strategy}
""".strip()
