import requests
import pandas as pd

def get_binance_data(symbol, interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        return df
    except Exception as e:
        print(f"Hata (get_binance_data): {e}")
        return None

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]

    if latest_rsi > 70:
        return "🔽 Ayı"
    elif latest_rsi < 30:
        return "🔼 Boğa"
    else:
        return "⏸ Nötr"

def calculate_macd(df, short=12, long=26, signal=9):
    short_ema = df["close"].ewm(span=short, adjust=False).mean()
    long_ema = df["close"].ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()

    if macd.iloc[-1] > signal_line.iloc[-1]:
        return "🔼 Boğa"
    elif macd.iloc[-1] < signal_line.iloc[-1]:
        return "🔽 Ayı"
    else:
        return "⏸ Nötr"

def calculate_ema(df, period=50):
    ema = df["close"].ewm(span=period, adjust=False).mean()
    current_price = df["close"].iloc[-1]
    current_ema = ema.iloc[-1]

    if current_price > current_ema:
        return "🔼 Boğa"
    elif current_price < current_ema:
        return "🔽 Ayı"
    else:
        return "⏸ Nötr"

def load_coin_list(filename="coin_list_updated.txt"):
    try:
        with open(filename, "r") as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{filename} bulunamadı.")
        return []
