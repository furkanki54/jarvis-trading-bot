import time
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_start_message():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Jarvis bot başlatıldı!")

if __name__ == "__main__":
    send_start_message()
    print("Jarvis bot çalışıyor...")
    while True:
        time.sleep(60)
