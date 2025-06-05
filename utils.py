import requests
import numpy as np

def get_binance_data(symbol, interval):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def calculate_rsi(closes, period=14):
    closes = np.array(closes)
    deltas = np.diff(closes)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100. - 100. / (1. + rs)

    for delta in deltas[period:]:
        upval = max(delta, 0)
        downval = -min(delta, 0)
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi = 100. - 100. / (1. + rs)

    return rsi

def calculate_ema(closes, period=50):
    return np.mean(closes[-period:])

def calculate_macd(closes, fast_period=12, slow_period=26, signal_period=9):
    closes = np.array(closes)
    ema_fast = np.convolve(closes, np.ones(fast_period)/fast_period, mode='valid')
    ema_slow = np.convolve(closes, np.ones(slow_period)/slow_period, mode='valid')
    macd_line = ema_fast[-1] - ema_slow[-1]
    signal_line = np.mean(ema_fast[-signal_period:])
    return macd_line, signal_line

def detect_golden_cross(ema50, ema200):
    return ema50 > ema200

def detect_death_cross(ema50, ema200):
    return ema50 < ema200

def load_coin_list(filename):
    with open(filename, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]
