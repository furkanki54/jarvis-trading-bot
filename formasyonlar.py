import requests
import numpy as np
from scipy.signal import argrelextrema

def get_price_data(symbol="BTCUSDT", interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    return [float(x[4]) for x in data]  # kapanış fiyatları

def find_trend_break(prices, window=5):
    prices = np.array(prices)

    # Dip ve tepe noktaları tespiti
    local_max_idx = argrelextrema(prices, np.greater, order=window)[0]
    local_min_idx = argrelextrema(prices, np.less, order=window)[0]

    # Yükselen trend: diplerden çizgi
    if len(local_min_idx) >= 2:
        x1, x2 = local_min_idx[-2], local_min_idx[-1]
        y1, y2 = prices[x1], prices[x2]
        if x2 != x1:
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            last_price = prices[-1]
            trend_line_price = slope * (len(prices) - 1) + intercept

            if last_price < trend_line_price * 0.995:
                return "📉 Yükselen trend çizgisi kırıldı", round(trend_line_price, 2), round(last_price, 2)

    # Düşen trend: tepe noktalarından çizgi
    if len(local_max_idx) >= 2:
        x1, x2 = local_max_idx[-2], local_max_idx[-1]
        y1, y2 = prices[x1], prices[x2]
        if x2 != x1:
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            last_price = prices[-1]
            trend_line_price = slope * (len(prices) - 1) + intercept

            if last_price > trend_line_price * 1.005:
                return "📈 Düşen trend çizgisi kırıldı", round(trend_line_price, 2), round(last_price, 2)

    return None, None, None
