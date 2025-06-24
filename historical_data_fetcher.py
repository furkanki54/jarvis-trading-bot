import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta

# ========================
COIN_LIST_FILE = "coin_list.txt"
DATA_DIR = "data"
INTERVALS = ["1d", "4h"]
START_DATE = "2020-01-01"
# ========================

def interval_to_ms(interval):
    if interval.endswith('m'):
        return int(interval[:-1]) * 60 * 1000
    elif interval.endswith('h'):
        return int(interval[:-1]) * 60 * 60 * 1000
    elif interval.endswith('d'):
        return int(interval[:-1]) * 24 * 60 * 60 * 1000
    else:
        raise ValueError("Geçersiz interval: " + interval)

def fetch_klines(symbol, interval, start_time):
    url = "https://fapi.binance.com/fapi/v1/klines"
    limit = 1500
    end_time = int(time.time() * 1000)
    data = []
    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "limit": limit
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"[HATA] {symbol} için veri alınamadı. Kod: {response.status_code}")
            break
        candles = response.json()
        if not candles:
            break
        data += candles
        last_time = candles[-1][0]
        start_time = last_time + interval_to_ms(interval)
        if start_time > end_time:
            break
        time.sleep(0.2)
    return data

def save_data_to_csv(symbol, interval, candles):
    columns = [
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ]
    df = pd.DataFrame(candles, columns=columns)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    filename = f"{DATA_DIR}/{symbol}_{interval}.csv"
    df.to_csv(filename, index=False)
    print(f"[KAYIT] {filename} kaydedildi.")

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    with open(COIN_LIST_FILE, "r") as file:
        coin_list = [line.strip().upper() for line in file.readlines()]

    for symbol in coin_list:
        for interval in INTERVALS:
            try:
                print(f"⏳ {symbol} ({interval}) verisi alınıyor...")
                start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
                start_ms = int(start_dt.timestamp() * 1000)
                candles = fetch_klines(symbol, interval, start_ms)
                save_data_to_csv(symbol, interval, candles)
            except Exception as e:
                print(f"[HATA] {symbol} {interval} – {e}")

if __name__ == "__main__":
    main()
