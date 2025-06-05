from helpers import analyze_coin
from config import TELEGRAM_TOKEN, CHAT_ID
import telebot
import time

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Takip edilecek coin listesi
coin_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "AVAXUSDT"]

# Sinyal eşiği (örneğin 9 ve üzeri)
THRESHOLD = 9.0

def check_and_alert():
    for coin in coin_list:
        print(f"⏳ {coin} kontrol ediliyor...")
        result = analyze_coin(coin)

        try:
            avg_line = [line for line in result.splitlines() if "Ortalama" in line][0]
            avg_score = float(avg_line.split(":")[1].split("/")[0].strip())
        except:
            avg_score = 0

        if avg_score >= THRESHOLD:
            alert_message = f"🚨 GÜÇLÜ TEKNİK SİNYAL TESPİT EDİLDİ!\n\n{result}"
            print(f"📢 {coin} için sinyal gönderiliyor...")
            bot.send_message(CHAT_ID, alert_message)
        else:
            print(f"❌ {coin} için sinyal eşiği aşılmadı. (Puan: {avg_score}/10)")

# Sonsuz döngü – Her saat başı kontrol
if __name__ == "__main__":
    print("📡 Sinyal tarayıcı başlatıldı.")
    while True:
        try:
            check_and_alert()
            print("⏲️ 1 saat uyku...")
            time.sleep(3600)  # 3600 saniye = 1 saat
        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")
            time.sleep(60)
