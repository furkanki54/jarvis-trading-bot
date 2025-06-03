import time

print("Jarvis bot başlatıldı...")

try:
    while True:
        print("Bot aktif...")  # Her döngüde log'a bir mesaj yaz
        time.sleep(30)         # 30 saniyede bir çalıştığını gösterir
except Exception as e:
    print("Bir hata oluştu:", e)
