# Jarvis Trading Bot (Binance Edition)

Bu bot, Binance API verilerini kullanarak belirli coin'lerdeki **fiyat ve hacim değişimlerini** analiz eder. Teknik göstergelerle birlikte değerlendirme yaparak **balina alımı gibi olağanüstü hareketleri tespit eder** ve Telegram grubuna otomatik sinyal gönderir.

---

## 📌 Özellikler

- ⏱ Her 100 saniyede bir analiz döngüsü
- 📈 RSI, EMA, MACD göstergeleriyle teknik analiz
- 📊 Fiyat ve hacim değişim oranı ile balina hareketi algılama
- 🤖 Telegram bot üzerinden otomatik sinyal iletimi
- 📃 İlk 10 coin (`coin_list_binance.txt`) üzerinden çalışır (örnek: BTCUSDT, ETHUSDT...)

---

## 🔧 Dosya Yapısı

- `main.py` → Botun ana çalışma dosyası
- `config.py` → Telegram bot token ve chat ID
- `coin_list_binance.txt` → İzlenecek coin listesi
- `requirements.txt` → Gerekli Python kütüphaneleri

---

## 🚀 Başlatmak için

```bash
pip install -r requirements.txt
python3 main.py
