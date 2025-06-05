import requests
import pandas as pd

def load_coin_list(filename):
    try:
        with open(filename, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def get_binance_data(symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines"
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

    last_rsi = rsi.iloc[-1]
    if last_rsi > 70:
        return "📈 Aşırı Alım"
    elif last_rsi < 30:
        return "📉 Aşırı Satım"
    elif last_rsi > 50:
        return "📈 Boğa"
    else:
        return "📉 Ayı"

def calculate_macd(df, short=12, long=26, signal=9):
    short_ema = df["close"].ewm(span=short, adjust=False).mean()
    long_ema = df["close"].ewm(span=long, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()

    if macd_line.iloc[-1] > signal_line.iloc[-1]:
        return "📈 Boğa"
    else:
        return "📉 Ayı"

def calculate_ema(df, short_period=9, long_period=21):
    short_ema = df["close"].ewm(span=short_period, adjust=False).mean()
    long_ema = df["close"].ewm(span=long_period, adjust=False).mean()

    if short_ema.iloc[-1] > long_ema.iloc[-1]:
        return "📈 Boğa"
    else:
        return "📉 Ayı"
