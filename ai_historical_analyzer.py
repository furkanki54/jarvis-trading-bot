import pandas as pd
from datetime import datetime

def analyze_historical_similarity(symbol, interval="1d", lookback_days=3):
    filename = f"data/{symbol}_{interval}.csv"
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        return "📛 Geçmiş veri bulunamadı."

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.sort_values("timestamp", inplace=True)

    recent_df = df.tail(lookback_days)
    if len(recent_df) < lookback_days:
        return "⏳ Yeterli veri yok."

    recent_closes = recent_df["close"].astype(float).values
    similarities = []

    for i in range(lookback_days, len(df) - lookback_days - 1):
        past = df.iloc[i - lookback_days:i]
        future = df.iloc[i + 1:i + 1 + lookback_days]
        past_closes = past["close"].astype(float).values

        if len(past_closes) != lookback_days or len(future) < lookback_days:
            continue

        diff = abs(recent_closes - past_closes).mean()
        similarity_score = 1 - (diff / max(recent_closes.max(), 1))

        if similarity_score > 0.97:
            past_close = past_closes[-1]
            future_close = future["close"].astype(float).values[-1]
            change_percent = (future_close - past_close) / past_close * 100
            similarities.append(change_percent)

    if not similarities:
        return "🧠 Geçmişte benzer yapı bulunamadı."

    avg_move = sum(similarities) / len(similarities)
    direction = "yükselmiş" if avg_move > 0 else "düşmüş"
    return f"📚 Geçmişte benzer yapılar {len(similarities)} kez görülmüş, ortalama %{abs(avg_move):.2f} oranında {direction}."
