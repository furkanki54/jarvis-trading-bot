import pandas as pd
from binance import Client

client = Client()

def get_ohlcv(symbol, interval="1h", limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['low'] = pd.to_numeric(df['low'])
    df['high'] = pd.to_numeric(df['high'])
    return df

def detect_support_resistance(symbol, interval="1h"):
    df = get_ohlcv(symbol, interval)
    closes = df['close'].tolist()
    support = min(closes[-20:])
    resistance = max(closes[-20:])
    return round(support, 2), round(resistance, 2)
