import requests
import pandas as pd

def load_coin_list(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def get_binance_data(symbol, interval="1h", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if isinstance(data, list):
            df = pd.DataFrame(data, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
            ])
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            return df
        return None
    except:
        return None

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(df, short=12, long=26, signal=9):
    short_ema = df["close"].ewm(span=short, adjust=False).mean()
    long_ema = df["close"].ewm(span=long, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line.iloc[-1], signal_line.iloc[-1]

def calculate_ema(df, short_period=9, long_period=21):
    short_ema = df["close"].ewm(span=short_period, adjust=False).mean()
    long_ema = df["close"].ewm(span=long_period, adjust=False).mean()
    return short_ema.iloc[-1], long_ema.iloc[-1]

def analyze_indicators(df):
    rsi = calculate_rsi(df)
    macd, signal = calculate_macd(df)
    ema_short, ema_long = calculate_ema(df)

    rsi_msg = ""
    if rsi > 70:
        rsi_msg = "RSI: Aşırı Alım (📈)"
    elif rsi < 30:
        rsi_msg = "RSI: Aşırı Satım (📉)"
    else:
        rsi_msg = f"RSI: {round(rsi, 2)}"

    macd_msg = "MACD: Boğa (📈)" if macd > signal else "MACD: Ayı (📉)"
    ema_msg = "EMA: Boğa (📈)" if ema_short > ema_long else "EMA: Ayı (📉)"

    return f"{rsi_msg}\n{macd_msg}\n{ema_msg}"

def analyze_price_volume(df, price_threshold=3.0, volume_threshold=50.0):
    if len(df) < 2:
        return None

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    price_change = ((latest["close"] - previous["close"]) / previous["close"]) * 100
    volume_change = ((latest["volume"] - previous["volume"]) / previous["volume"]) * 100

    if abs(price_change) >= price_threshold and abs(volume_change) >= volume_threshold:
        direction = "yükseliş" if price_change > 0 else "düşüş"
        return f"🚨 Anormal Hacim & Fiyat {direction.upper()} 🚨\nFiyat değişimi: %{price_change:.2f}, Hacim değişimi: %{volume_change:.2f}"
    return None
